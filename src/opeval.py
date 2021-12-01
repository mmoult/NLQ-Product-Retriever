
class OperatorEvaluator(object):
    '''
    Receives a list of typed values and saves the resulting parsed structure into
    result. Result is itself some relation or a value. All relations are inherently
    recursive, and may be composed of other relations or values.
    '''

    def __init__(self, typed):
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
                            at = self.__findEnd(typed, i+1, 1)
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
                            left = self.__findEnd(typed, i-1, -1)
                            right = self.__findEnd(typed, i+1, 1)
                            if left != -1 and right != -1:
                                lhs = []
                                for j in range(left, i):
                                    lhs.append(typed.pop(j))
                                i -= len(lhs)
                                rhs = []
                                for j in range(i, right+1):
                                    rhs.append(typed.pop(j))
                                typed[i] = OrRelation(lhs, rhs) if rnd==1 else AndRelation(lhs, rhs)
                i += 1
        self.result = typed
    
    
    def __findEnd(self, typed, start, iterate):
        # Type I and Type II end immediately, but type III can be up to 2 (for the number and unit). The chain
        # is broken by any Type IV in between.
        # We do not have to worry about bounds, since not applied to bounds was applied during standardization.
        if start < 0 or start >= len(typed):
            return -1
        if isinstance(typed[start], OperatorRelation):
            return start
        if typed[start][1] != 3:
            return start
        start += iterate
        if start < 0 or start >= len(typed) or isinstance(typed[start], OperatorRelation) or typed[start][1] != 3:
            return start - iterate
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
