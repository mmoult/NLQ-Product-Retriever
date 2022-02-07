import src.opeval as opeval
import math
from src.content_match import Similarity

class RelevanceRanker(object):
    
    def __init__(self, constr):
        self.rows = constr[0].dat
        self.fieldAt = dict()
        
        # We should build the requirements into a more readable structure
        self.reqs = [[], [], []]
        for i in range(0, 3):
            for strReq in constr[i+1]:
                self.reqs[i].append(self.__parseGroup(strReq))
        
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
                if len(value) == 0: # cannot content match on nothing
                    return 0
                exp = comp.vals[0]
                # We need to modify exp to be useful to us, since it currently has delimiting " and % symbols
                exp = exp[2:len(exp) - 2]
                if exp == value:
                    return 1
                # otherwise, we have to perform a partial matching approach...
                # We modify exp even further to remove the extra padding spaces
                exp = exp[1:len(exp) - 1]
                distance = -1
                if self.similarity is not None:
                    node = self.similarity.valueNode(comp.attr, exp)
                    # there may be no similarity matches for either the attribute or value
                    if node is not None:
                        # the typical offset is related to the number of nodes in the graph. 
                        typical = len(self.similarity.graphs[comp.attr].nodes) / 2
                        # If there are any related, then return the similarity value
                        for edge in node.connections:
                            if value in (' ' + edge.toNode.name + ' '):
                                distance = edge.cost
                                break
                if distance == -1:
                    return 0 # since distance was not actually set
            else:
                # All other operations use numbers
                act = float(value)
                exp = float(comp.vals[0])
                # Find the divisor, which will effectively determine how much the difference between actual and
                #  expected should be penalized. Years are an interesting attribute, because for cars, motorcycles,
                #  and some other products, they are closer to a Type II than a Type III in that the exact year
                #  may be important for the style.
                if comp.attr == 'year':
                    # TODO: I had to decide some value to modify years since they are disproportionately
                    # larger than their use space (which is approx from 1950 - 2022)
                    typical = 10 
                else:
                    typical = exp
                
                if comp.operation == '=':
                    distance = math.fabs(exp - act)
                # Often with ranges, we want the extreme. There is no way to take that into account without
                # giving some form of extra credit, which would be a controversial decision.
                elif comp.operation == '>':
                    if act > exp:
                        return 1 # This is where we would calculate extra credit score
                    distance = exp - (act - 0.1)
                elif comp.operation == '>=':
                    if act >= exp:
                        return 1 
                    distance = exp - act
                elif comp.operation == '<':
                    if act < exp:
                        return 1 # This is where we would calculate extra credit score
                    distance = (act + 0.1) - exp
                elif comp.operation == '<=':
                    if act <= exp:
                        return 1 # This is where we would calculate extra credit score
                    distance = act - exp
                elif comp.operation == 'BETWEEN':
                    lo = exp
                    hi = float(comp.vals[1])
                    exp = (lo + hi) / 2
                    if act >= lo and act <= hi:
                        return 1
                    if act < lo:
                        distance = lo - act
                    elif act > hi:
                        distance = act - hi
                else:
                    raise Exception('Unknown operation "' + comp.operation + '"!')
            
            # the more distant something is from the desired, the less the score decreases relatively.
            # This is not a linear model of score depreciation. Instead, we use an exponential decay.
            return .5 ** (distance / (typical / 5))
    
    
    def rank(self, results, limit):
        # Each type of data receives a certain weight:
        #  1: 1, 2: .5, 3:.25
        # Thus, an exact match in type III will count similarly to a bad match on type I
        weights = [1, .75, .5]
        
        # We need to score every record in results
        scores = []
        for record in results:
            score = 0
            for i in range(0, 3):
                for req in self.reqs[i]:
                    score += weights[i] * self.getScore(req, record)
            # typically we would normalize scores, but they are only used internally, compared to other records with the same reqs
            scores.append([score, record])
        
        scores.sort(key=lambda entry : entry[0], reverse=True)
        scores = scores[:limit]
        return scores#[entry[1] for entry in scores]
        