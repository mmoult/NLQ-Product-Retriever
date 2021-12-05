
class OperatorEvaluator(object):
    '''
    Receives a list of typed values and saves the resulting parsed structure into
    result. Result is itself some relation or a value. All relations are inherently
    recursive, and may be composed of other relations or values.
    '''

    def __init__(self, typed, isOp):
        # To maintain precedence rules, we need to process the operators sequentially.
        # First not, then or, then and.
        for rnd in range(3):
            i = 0
            while i < len(typed):
                if not isinstance(typed[i], OperatorRelation):
                    # Search for not
                    if rnd == 0:
                        if typed[i][0] == 'not' or typed[i][0] == 'no' or typed[i][0] == '!=':
                            # The next token is included in the structure
                            at = self.__findEnd(typed, i+1, 1, isOp)
                            if at != -1:
                                ls = []
                                for j in range(i+1, at+1):
                                    ls.append(typed.pop(j))
                                typed[i] = NotRelation(ls)
                    else: # Searching for an 'or' or 'and'
                        # And and Or have the same format, just diff comparisons and results
                        compare = 'or' if rnd == 1 else 'and'
                        if typed[i][0] == compare:
                            # find the left and right parts
                            left = self.__findEnd(typed, i-1, -1, isOp)
                            right = self.__findEnd(typed, i+1, 1, isOp)
                            if left != -1 and right != -1:
                                lhs = []
                                for _ in range(left, i):
                                    lhs.append(typed.pop(left))
                                i -= len(lhs)
                                rhs = []
                                for _ in range(i+1, right):
                                    rhs.append(typed.pop(i+1))
                                typed[i] = OrRelation(lhs, rhs) if rnd==1 else AndRelation(lhs, rhs)
                i += 1
        self.result = typed
    
    
    def __findEnd(self, typed, start, iterate, isOp):
        from src.typify import isNumeric
        # Type I and Type II end immediately, but type III can be longer (since it may consist of the value number, 
        # the unit, and some bound. The chain is broken by any other Type IV in between.
        if start < 0 or start >= len(typed):
            return -1
        if isinstance(typed[start], OperatorRelation):
            return start
        
        bound = False
        if typed[start][1] != 3:
            if isOp(typed[start][0]):
                bound = True
            else:
                return start - (iterate if typed[start][1] == 4 else 0)
        
        value = False
        unit = False
        while not (value and unit and bound):
            start += iterate
            abort = False
            if start < 0 or start >= len(typed) or isinstance(typed[start], OperatorRelation):
                abort = True
            elif typed[start][1] != 3:
                if not bound and isOp(typed[start][0]):
                    bound = True
                else:
                    abort = True
            # at this point in the chain, the typed must be a Type 3, so we look for a number or a unit
            else:
                number = isNumeric(typed[start][0])
                if not value and number:
                    value = True
                elif not unit and not number:
                    unit = True
                else:
                    abort = True
            if abort:
                return start + iterate
        return start


from abc import ABC, abstractmethod
class OperatorRelation(ABC):
    '''The abstract base class for all relations'''
    
    @abstractmethod
    def operator(self):
        pass


class OrRelation(OperatorRelation):
    
    def __init__(self, left, right):
        self.left = left
        self.right = right
        
    def operator(self):
        return 'OR'


class AndRelation(OperatorRelation):
    
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def operator(self):
        return 'AND'


class NotRelation(OperatorRelation):
    
    def __init__(self, notted):
        self.notted = notted
    
    def operator(self):
        return 'NOT'
    


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
