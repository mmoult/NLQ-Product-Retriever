import src.opeval as opeval
import math
from src.content_match import Similarity

class RelevanceRanker(object):
    
    def __init__(self, constr):
        self.rows = constr[0].dat
        self.fieldAt = dict()
        
        # We should build the requirements into a more readable structure
        strReqs = constr[1] + constr[2] + constr[3]
        self.reqs = []
        for strReq in strReqs:
            self.reqs.append(self.__parseGroup(strReq))
        
        try: # Attempt to build the word similarity graphs for this table
            self.similarity = Similarity(constr[0].name)
        except: # If this domain does not have word similarity matches
            self.similarity = None # just put a placeholder so we don't crash on reference
    
    
    class Unit(object):
        def __init__(self, attr, operation, *vals):
            self.attr = attr
            self.operation = operation
            self.vals = vals
    
    
    def __parseGroup(self, req): # returns a Unit or Operation composed of units
        # each requirement is built of operators (AND, OR, and NOT) and unit primitives ("attr op val" or "attr BETWEEN val1 AND val2")
        i = 0
        temp = None
        currOp = None
        while i < len(req):
            if req[i] == '(':
                # We are starting some group
                end = self.__findEnd(req, i)
                temp = self.__parseGroup(req[i+1:end])
                i = end
            elif req[i:i+3] == 'NOT':
                currOp = opeval.NotRelation(None)
                i += 3
            elif req[i:i+3] == 'AND':
                currOp = opeval.AndRelation(None, None)
                i += 3
            elif req[i:i+2] == 'OR':
                currOp = opeval.OrRelation(None, None)
                i += 2
            elif req[i] != ' ':
                # here we found a unit!
                # attr goes until the next space
                end = req.find(' ', i)
                attr = req[i:end]
                # operation goes from end to the next space
                i = end + 1
                end = req.find(' ', i)
                operation = req[i:end]
                end += 1
                i = end
                # Now things get a little tricky. Values can come last, so we may not find a space
                # Furthermore, space is no longer a sure-fire bet, since there can be spaces in strings
                inString = False
                while end < len(req):
                    if req[end] == '"':
                        inString = not inString
                    elif req[end] == ' ' and not inString:
                        break
                    end += 1
                val1 = req[i:end]
                i = end
                if operation != 'BETWEEN':
                    temp = self.Unit(attr, operation, val1)
                else:
                    # we need to find the other value
                    space = req.find(' ', i+1) # we know that there are no strings here luckily :)
                    end = len(req) if space == -1 else space
                    val2 = req[i:end]
                    i = end
                    temp = self.unit(attr, operation, val1, val2)
            else: # space
                i += 1
                continue # nothing changed, so we don't have to perform checks
            
            # at the end here, we perform some checks
            if temp is not None and currOp is not None and isinstance(currOp, opeval.NotRelation):
                currOp.notted = temp
                temp = currOp
                currOp = None
            elif temp is not None and currOp is not None:
                # we must insert temp into currOp, which is not a NOT
                if currOp.left is None:
                    currOp.left = temp # move the temp into the left slot of the operation
                    temp = None
                else:
                    currOp.right = temp
                    temp = currOp # move the operation to the temporary slot
                    currOp = None
            # then we move to the next index
            i += 1
        return temp
    
    
    def __findEnd(self, req, index):
        end = index + 1
        levels = 0
        while end < len(req):
            if req[end] == '(':
                levels += 1
            elif req[end] == ')':
                if levels == 0:
                    return end
                # otherwise, we decrease level
                levels -= 1
            end += 1
        return end
    
    
    def findEntryIndex(self, fieldName):
        if fieldName in self.fieldAt:
            return self.fieldAt[fieldName]
        i = 0
        for row in self.rows:
            if row[0][0].lower() == fieldName.lower():
                self.fieldAt[fieldName] = i
                return i
            i += 1
        return -1 # could not be found!
    
    
    def getScore(self, comp, entry):
        # If we have a component that is a operator, then we can perform some simple logical operations
        if isinstance(comp, opeval.OrRelation):
            # OR returns the higher of the two scores
            return max(self.getScore(comp.left, entry), self.getScore(comp.right, entry))
        elif isinstance(comp, opeval.AndRelation):
            # AND returns the lower of the two scores
            return min(self.getScore(comp.left, entry), self.getScore(comp.right, entry))
        elif isinstance(comp, opeval.NotRelation):
            # NOT can simply return 1 - score
            return 1 - self.getScore(comp.notted, entry)
        else:
            # regular clause to evaluate. This is the hardest part
            at = self.findEntryIndex(comp.attr)
            value = entry[at]
            if comp.operation == 'LIKE':
                exp = comp.vals[0]
                # We need to modify exp to be useful to us, since it currently has delimiting " and % symbols
                exp = exp[2:len(exp) - 2]
                if exp in value or value in exp:
                    return 1
                # otherwise, we have to perform a partial matching approach...
                # We modify exp even further to remove the extra padding spaces
                exp = exp[1:len(exp) - 1]
                node = self.similarity.valueNode(comp.attr, exp)
                # there may be no similarity matches for either the attribute or value
                if node is not None:
                    # TODO: I experimentally chose edgeDiv, but we may be able to find a more scientific approach
                    edgeDiv = 5 # Edge cost penalty divisor. The larger this number, the less the weight read from file is
                    # If there are any related, then return the similarity value
                    for edge in node.connections:
                        if value in (' ' + edge.toNode.name + ' '):
                            return 1 - edge.cost / edgeDiv if math.fabs(edge.cost) < edgeDiv else 0
                return 0
            # All other operations use numbers
            act = float(value)
            exp = float(comp.vals[0])
            # Find the divisor, which will effectively determine how much the difference between actual and
            #  expected should be penalized. Years are an interesting attribute, because for cars, motorcycles,
            #  and some other products, they are closer to a Type II than a Type III in that the exact year
            #  may be important for the style.
            if comp.attr == 'year':
                divisor = 8 # TODO: I had to decide some value to modify the score penalty
            else:
                divisor = exp
            
            if comp.operation == '=':
                score = 1 - math.fabs(exp - act)/divisor
            # Often with ranges, we want the extreme. There is no way to take that into account without
            # giving some form of extra credit, which would be a controversial decision.
            elif comp.operation == '>':
                if act > exp:
                    return 1 # This is where we would calculate extra credit score
                score = 1 - (exp - (act - 0.1))/divisor
            elif comp.operation == '>=':
                if act >= exp:
                    return 1 
                score = 1 - (exp - act)/divisor
            elif comp.operation == '<':
                if act < exp:
                    return 1 # This is where we would calculate extra credit score
                score = 1 - ((act + 0.1) - exp)/divisor
            elif comp.operation == '<=':
                if act <= exp:
                    return 1 # This is where we would calculate extra credit score
                score = 1 - (act - exp)/divisor
            elif comp.operation == 'BETWEEN':
                lo = exp
                hi = float(comp.vals[1])
                exp = (lo + hi) / 2
                if act >= lo and act <= hi:
                    return 1
                if act < lo:
                    score = 1 - (lo - act)/divisor
                elif act > hi:
                    score = 1 - (act - hi)/divisor
            else:
                raise Exception('Unknown operation "' + comp.operation + '"!')
            if score < 0:
                score = 0
            return score
    
    
    def rank(self, results, limit):
        # We need to score every record in results
        scores = []
        for record in results:
            score = 0
            for req in self.reqs:
                score += self.getScore(req, record)
            # typically we would normalize scores, but they are only used internally, compared to other records with the same reqs
            scores.append([score, record])
        
        scores.sort(key=lambda entry : entry[0], reverse=True)
        scores = scores[:limit]
        return scores #[entry[1] for entry in scores]
        