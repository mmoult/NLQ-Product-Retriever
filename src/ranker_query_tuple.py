import src.opeval as opeval
import math
from src.content_match import Similarity
from scipy import spatial
import math
from src.partial import PartialMatcher


class RelevanceRanker_query_tuple(object):
    def __init__(self, constr):
        self.rows = constr[0].dat
        self.fieldAt = dict()
        # We should build the requirements into a more readable structure
        self.reqs = [[], [], []]
        for i in range(0, 3):
            for strReq in constr[i + 1]:
                self.reqs[i].append(self.__parseGroup(strReq))

        try:  # Attempt to build the word similarity graphs for this table
            self.similarity = Similarity(constr[0].name)
        except:  # If this domain does not have word similarity matches
            self.similarity = None  # just put a placeholder so we don't crash on reference

    class Unit(object):
        def __init__(self, attr, operation, *vals):
            self.attr = attr
            self.operation = operation
            self.vals = vals

    def __parseGroup(self, req):  # returns a Unit or Operation composed of units
        # each requirement is built of operators (AND, OR, and NOT) and unit primitives ("attr op val" or "attr BETWEEN val1 AND val2")
        i = 0
        temp = None
        currOp = None
        while i < len(req):
            if req[i] == '(':
                # We are starting some group
                end = self.__findEnd(req, i)
                temp = self.__parseGroup(req[i + 1:end])
                i = end
            elif req[i:i + 3] == 'NOT':
                currOp = opeval.NotRelation(None)
                i += 3
            elif req[i:i + 3] == 'AND':
                currOp = opeval.AndRelation(None, None)
                i += 3
            elif req[i:i + 2] == 'OR':
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
                    space = req.find(' ', i + 1)  # we know that there are no strings here luckily :)
                    end = len(req) if space == -1 else space
                    val2 = req[i:end]
                    i = end
                    temp = self.unit(attr, operation, val1, val2)
            else:  # space
                i += 1
                continue  # nothing changed, so we don't have to perform checks

            # at the end here, we perform some checks
            if temp is not None and currOp is not None and isinstance(currOp, opeval.NotRelation):
                currOp.notted = temp
                temp = currOp
                currOp = None
            elif temp is not None and currOp is not None:
                # we must insert temp into currOp, which is not a NOT
                if currOp.left is None:
                    currOp.left = temp  # move the temp into the left slot of the operation
                    temp = None
                else:
                    currOp.right = temp
                    temp = currOp  # move the operation to the temporary slot
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
        return -1  # could not be found!

    def getScore(self, comp, entry, target_tuple, record_tuple, columns):
        # print(comp, entry, "comp, entry")
        # If we have a component that is a operator, then we can perform some simple logical operations
        if isinstance(comp, opeval.OrRelation):
            # OR returns the higher of the two scores
            return max(self.getScore(comp.left, entry, target_tuple, record_tuple, columns), self.getScore(comp.right, entry, target_tuple, record_tuple, columns))
        elif isinstance(comp, opeval.AndRelation):
            # AND returns the lower of the two scores
            return min(self.getScore(comp.left, entry, target_tuple, record_tuple, columns), self.getScore(comp.right, entry, target_tuple, record_tuple, columns))
        elif isinstance(comp, opeval.NotRelation):
            # NOT can simply return 1 - score
            return 1 - self.getScore(comp.notted, entry, target_tuple, record_tuple, columns)
        else:

            # regular clause to evaluate. This is the hardest part
            at = self.findEntryIndex(comp.attr)
            value = entry[at]
            if isinstance(value, str):
                value = value.lower()
            if comp.operation == 'LIKE':

                target_super_tuple = target_tuple[comp.attr]
                records_super_tuple = record_tuple[comp.attr][value.strip()]

                target_set = set(target_super_tuple)
                record_set = set(records_super_tuple)
                n = 0
                for key in target_set.intersection(record_set):
                    n += min(target_super_tuple[key], records_super_tuple[key])
                d = sum(target_super_tuple.values())+ sum(records_super_tuple.values())
                score = n/d
                # print(score)
                # return score
            else:
                # All other operations use numbers
                act = float(value)
                exp = float(comp.vals[0])
                # Find the divisor, which will effectively determine how much the difference between actual and
                #  expected should be penalized. Years are an interesting attribute, because for cars, motorcycles,
                #  and some other products, they are closer to a Type II than a Type III in that the exact year
                #  may be important for the style.
                return 1 - abs(exp - act)/exp
            # the more distant something is from the desired, the less the score decreases relatively.
            # This is not a linear model of score depreciation. Instead, we use an exponential decay.
            return 0

    def rank(self, target_tuple, record_tuple,results,columns, limit):
        # Each type of data receives a certain weight:
        #  1: 1, 2: .5, 3:.25
        # Thus, an exact match in type III will count similarly to a bad match on type I
        # weights = [1, .5, .25]

        # We need to score every record in results

        scores = []
        for record in results:
            score = 0
            for i in range(0, 3):
                for req in self.reqs[i]:
                    score +=  self.getScore(req, record,target_tuple, record_tuple, columns)
            # typically we would normalize scores, but they are only used internally, compared to other records with the same reqs
            scores.append([score, record])

        scores.sort(key=lambda entry: entry[0], reverse=True)
        scores = scores[:limit]
        return [entry[1] for entry in scores]
