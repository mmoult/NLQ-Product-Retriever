'''
Created on Oct 1, 2021

'''
import string

class DataExtractor(object):
    '''
    Extracts different type of data from the text
    '''

    typeI = None
    typeII = None
    typeIII = None
    
    def extract(self, text: string):
        # first order of business is going to be to tokenize the text
        tokens = text.split(' ')
        
        # each token is going to be evaluated by the different heuristics
        for token in tokens:
            print(token)
            pass
    
    
    def __isPlural(self, token: string) -> bool:
        # we may need to use Stanford POS to know this for sure
        pass
    
    def __isCapital(self, token: string) -> bool:
        return len(token) > 0 and token[0] in string.ascii_uppercase
    
    def __isAdjective(self, token: string) -> bool:
        # we need Stanford POS here
        pass
    
    def __isMeasurement(self, token: string) -> bool:
        pass
    
    def __isAlphaNumeric(self, token: string) -> bool:
        pass
    
    def __isLocation(self, token: string) -> bool:
        pass
    
    def __isAcronym(self, token: string) -> bool:
        pass
        