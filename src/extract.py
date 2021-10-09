'''
Created on Oct 1, 2021

'''
import string

class DataExtractor(object):
    '''
    Extracts different type of data from the text
    '''

    def __init__(self):
        self.typeI = None
        self.typeII = None
        self.typeIII = None
        
        placeFile = open("../place-names.txt")
        wholeList = placeFile.read()
        self.placeNames = wholeList.split('\n')
        for name in self.placeNames:
            name = name.lower()
        placeFile.close()
        
        measureFile = open("../measure-units.txt")
        allMeasure = measureFile.read()
        self.measureUnits = allMeasure.split('\n')
        for name in self.measureUnits:
            name = name.lower()
        measureFile.close()
    
    
    def classify(self, text: string):
        # running the Stanford POS Tagger from NLTK
        import nltk
        ''' Needed NLTK downloads to run the rest:
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        '''
        
        # first order of business is going to be to tokenize the text
        tokens = nltk.word_tokenize(text)
        # we also need to analyze the part of speech for each token
        pos_tagged = nltk.pos_tag(tokens)        
        
        # each token is going to be evaluated by the different heuristics
        # https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
        for token in pos_tagged:
            print(token, self.__isPlural(token), self.__isCapital(token), self.__isAdjective(token), self.__isMeasurement(token), self.__isAlphaNumeric(token), self.__isLocation(token), self.__isAcronym(token))
            # Here we should be identifying the types that each token is and place it correctly
    
    
    def __isPlural(self, token) -> bool:
        # The types that are plural are NNS (noun, plural) and NNPS (Proper noun, plual)
        return token[1] == 'NNS' or token[1] == 'NNPS'
    
    def __isCapital(self, token) -> bool:
        # in the tuple, the first element is the token itself, the second is the part of speech
        return len(token[0]) > 0 and token[0][0] in string.ascii_uppercase
    
    def __isAdjective(self, token) -> bool:
        # All JJ types (JJ, JJR, and JJS) are adjectives
        return 'JJ' in token[1]
    
    def __isMeasurement(self, token) -> bool:
        # https://hobbyprojects.com/dictionary_of_units.html
        return token[0].lower() in self.measureUnits
    
    def __isAlphaNumeric(self, token) -> bool:
        import functools
        alpha = functools.reduce(lambda x, y: x or y in string.ascii_letters, token[1], False)
        numeric = functools.reduce(lambda x, y: x or y in string.digits, token[1], False)
        return alpha and numeric
    
    def __isLocation(self, token) -> bool:
        # https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population
        return token[0].lower() in self.placeNames
    
    def __isAcronym(self, token) -> bool:
        # TODO come back to this with common abbreviations for the different categories
        pass
        