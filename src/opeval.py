
class OperatorEvaluator(object):
    '''
    Receives a list of typed values and saves the resulting parsed structure into
    result. Result is itself some relation or a value. All relations are inherently
    recursive, and may be composed of other relations or values.
    '''

    def __init__(self, typed, isOp):
        # To maintain precedence rules, we need to process the operators sequentially.
        # First and, then or, and lastly not.
        for rnd in range(3):
            i = 0
            while i < len(typed):
                if not isinstance(typed[i], OperatorRelation):
                    # Search for not
                    if rnd == 2:
                        if typed[i][0] == 'not' or typed[i][0] == 'no' or typed[i][0] == '!=':
                            # The next token is included in the structure
                            at = self.__findEnd(typed, i+1, 1, isOp, -1)
                            if at != -1:
                                ls = []
                                for j in range(i+1, at+1):
                                    ls.append(typed.pop(j))
                                typed[i] = NotRelation(ls, isOp)
                    else: # Searching for an 'or' or 'and'
                        # And and Or have the same format, just diff comparisons and results
                        compare = 'or' if rnd == 1 else 'and'
                        if typed[i][0] == compare:
                            # find the left and right parts
                            left = self.__findEnd(typed, i-1, -1, isOp, -1)
                            # find the type of the left so that we can try to match on the right
                            leftSearch = typed[left]
                            while isinstance(leftSearch, OperatorRelation):
                                if isinstance(leftSearch, NotRelation):
                                    leftSearch = leftSearch.notted[-1]
                                else:
                                    leftSearch = leftSearch.right[-1] # we want to get the closest to the relation on the right (though from the left)
                            leftType = leftSearch[1]
                            right = self.__findEnd(typed, i+1, 1, isOp, leftType)
                            if left != -1 and right != -1:
                                lhs = []
                                for _ in range(left, i):
                                    lhs.append(typed.pop(left))
                                i -= len(lhs)
                                rhs = []
                                for _ in range(i+1, right+1-len(lhs)):
                                    rhs.append(typed.pop(i+1))
                                typed[i] = OrRelation(lhs, rhs, isOp) if rnd==1 else AndRelation(lhs, rhs, isOp)
                i += 1
        self.result = typed
    
    
    def __findEnd(self, typed, start, iterate, isOp, typeMatch):
        from src.typify import isNumeric
        if start < 0 or start >= len(typed):
            return -1
        if isinstance(typed[start], OperatorRelation):
            return start
        
        # Type I and Type II end immediately, but type III can be longer (since it may consist of the value number, 
        #  the unit, and some bound. The chain is broken by any other Type IV in between.
        # An exception to this rule is for type matching. It is typical for 'or' and 'and' to separate components of
        #  the same type. For example, "honda or red toyota" would be interpreted as (honda) or (red toyota).
        #  Theoretically, we could keep looking for the match until the end of the list, but this is bound to generate
        #  a number of false positives. Therefore, we only look for the token after the first found.
        # We may want to continue the search in case of another match. For example, in "toyota or honda odyssey", we
        #  find the match immediately in honda, but odyssey is another Type 1 value that goes with honda.
        # Then we may ask why such a match cannot occur without a matching. Why would "honda odyssey or toyota" not
        #  yield (honda odyssey) or (toyota)? It could, but we also face problems, even within Type I, where run-ons
        #  should not be considered, such as "honda odyssey or pilot" -> honda (odyssey or pilot).
        # Thus, run-ons should only be considered if the type is expected. Furthermore, run-ons should only be 
        #  considered for Type I values. This is because other type values are often more independent than Type I
        #  values. For example, odyssey only makes sense with honda, but color or mileage are universal to all cars.
        import math
        maxTolerance = math.inf # We decided that we want to search for the matching type, regardless of distance.
        tolerance = 0
        currType = -1
        
        i = start       # The iterator index
        # The first index where tolerance is necessary. If the expected type is not found, we revert back to this
        firstBreak = -1
        value = False   # whether a value has been set for this type 3
        unit = False    # whether a unit has been set "
        bound = False   # whether a bound (<, >, etc) has been set "
        
        while True:
            if i < 0 or i >= len(typed):
                break
            if isinstance(typed[i], OperatorRelation):
                # We never include operator relations if they are beyond the first searched index
                break
            
            newFound= typed[i][1]
            
            # Now we perform a case analysis for the current type and what is found
            if currType == 1:
                # Type I values are sticky if they are expected
                if typeMatch == 1 and newFound == 1:
                    i += iterate
                    continue
                # Otherwise, we continue to the next type
            # Type 2 values are never sticky, so we don't need to handle them separately
            if currType == 3 or (currType == -1 and newFound == 3):
                fine = True
                if isNumeric(typed[i][0]) and not value:
                    value = True
                elif isOp(typed[i][0]) and not bound:
                    bound = True
                elif not unit and newFound == 3:
                    unit = True
                else:
                    fine = False
                if fine:
                    currType = 3
                    i += iterate
                    continue
            
            if currType == -1:
                currType = newFound # set this the first time
                i += iterate
                continue
            
            # If we made it here, that means that we did not continue the same type.
            # Typically we only continue if we are expecting some type. However, there is a
            #  special case to continue if we encounter some noun description chunk.
            if typeMatch == -1 and iterate < 0 and currType == 1 and (newFound == 2 or newFound == 3):
                # Type I values are typically nouns. In the English language, adjectives and
                #  other descriptors precede the nouns they describe. Thus, if we had a Type
                #  I value and we are going backwards, then we can encounter some 2 or 3
                #  next without breaking out.
                typeMatch = newFound
            
            if typeMatch != -1 and currType != typeMatch:
                if tolerance == 0:
                    firstBreak = i
                # If we are looking for something specific, we can have tolerance
                tolerance += 1
                if tolerance > maxTolerance:
                    # We have exceeded our tolerance level, so we need to break
                    typeMatch = -1 # indicate that the match was not found
                    break
                else: # We will consider this type before we need the match
                    currType = newFound
                    if currType == 3:
                        value = False
                        unit = False
                        bound = False
                        # Otherwise, we can just continue to the next token
            else:
                # We have no tolerance if we have nothing to match.
                break
            i += iterate # continue to the next index. This is the iterative element of the loop
        
        # If the match is -1 and the first break is not, then our tolerance was exceeded and we
        #  need to revert back to the first break. firstBreak can only be set if typeMatch is not
        #  -1, but typeMatch is set to -1 if we don't find our match. 
        if typeMatch == -1 and firstBreak != -1:
            # If we did not end up finding the expected match, then our tolerance was useless
            i = firstBreak
        return i - iterate


from abc import ABC, abstractmethod
class OperatorRelation(ABC):
    '''The abstract base class for all relations'''
    
    @abstractmethod
    def operator(self):
        pass
    
    def __repr__(self): # printing a list prints the representation of the elements rather than the string
        return self.__str__()


class OrRelation(OperatorRelation):
    
    def __init__(self, left, right, isOp = None):
        if isOp != None:
            OperatorEvaluator(left, isOp)
            OperatorEvaluator(right, isOp)
        self.left = left
        self.right = right
        
    def operator(self):
        return 'OR'
    
    def __str__(self):
        return "{" + str(self.left) + "} OR {" + str(self.right) + "}"


class AndRelation(OperatorRelation):
    
    def __init__(self, left, right, isOp = None):
        if isOp != None:
            OperatorEvaluator(left, isOp)
            OperatorEvaluator(right, isOp)
        self.left = left
        self.right = right
    
    def operator(self):
        return 'AND'
    
    def __str__(self):
        return "{" + str(self.left) + "} AND {" + str(self.right) + "}"


class NotRelation(OperatorRelation):
    
    def __init__(self, notted, isOp = None):
        if isOp != None:
            OperatorEvaluator(notted, isOp)
        self.notted = notted
    
    def operator(self):
        return 'NOT'
    
    def __str__(self):
        return "NOT {" + str(self.notted) + "}"



class OperatorHandler():
    import string
    def __init__(self):
        # We want to load some data from files containing boundary words
        #  and superlative words.
        self.bounders, self.boundApps = self.__loadSynonymFile("boundary-synonyms")
        self.superlatives, self.superApps = self.__loadSynonymFile("superlatives-synonyms")
    
    
    def __loadSynonymFile(self, fileName:string):
        from pathlib import Path
        synFile = open(str(Path(__file__).parent) + "/../" + fileName + ".txt", encoding='utf-8')
        synList = []
        appDict = None
        currBound = []
        currSym = None
        for line in synFile:
            if appDict is None:
                line = line[0:-1] # to remove the trailing new line
                if len(line) == 0:
                    if len(currBound) > 0:
                        synList.append([currSym, currBound])
                        currBound = []
                    currSym = None
                else:
                    if line[0] == '-': # The dash barrier marks the end of the boundary synonyms
                        appDict = {}
                    elif currSym is None: # the new symbol is set
                        currSym = line
                    else:
                        currBound.append(line)
            else:
                # For applications. These are definitions of parenthesized numbers (which are used by boundary synonyms)
                firstEnd = line.find(' ')
                # The first token is the application defined
                defed = line[0:firstEnd]
                # All other tokens ought to be separated by ;
                split = line[firstEnd+1:-1].split('; ')
                appDict.update({defed: split})
        if len(currBound) > 0:
            synList.append([currSym, currBound])
        synFile.close()
        
        return synList, appDict
    
    
    def isOperation(self, opSet, x:string) -> bool:
        for operation in opSet:
            sym = operation[0]
            # if the bounding symbol is the first in the string, then we know it is a bounding operation
            if x.find(sym) == 0 and (len(x) == len(sym) or x[len(sym)]==' '): 
                return sym
        return None
    
    def isBoundOperation(self, x:string) -> bool:
        return self.isOperation(self.bounders, x)
    
    def isSuperlative(self, x:string) -> bool:
        return self.isOperation(self.superlatives, x)
