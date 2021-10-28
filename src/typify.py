'''
Created on Oct 16, 2021

@author: Matthew Moulton
'''
import string
import nltk
from src.trie import verify


class TypeExtractor(object):
    '''
    This class will use the trie structure to typify each of the words in the query.
    The types available for use are Type I (identification), Type II (attribute values),
    Type III (numeric values and labels), and Type IV (useless filler words).
    '''

    def __init__(self):
        '''
        This is where we will need to construct all the associated trie structures.
        They are all nicely bundled in the TypeVerifier class
        '''
        self.verifier = verify.TypeVerifier()


    def typify(self, text: string, domain) -> [[string, int]]:
        # running the Stanford POS Tagger from NLTK
        ''' Needed NLTK downloads to run:
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        '''

        # first order of business is going to be to tokenize the text
        tokens = nltk.word_tokenize(text)
        # we also need to analyze the part of speech for each token
        pos_tagged = nltk.pos_tag(tokens)

        # each token will be compared with the trie structure created in the constructor
        ret = []
        for token in pos_tagged:
            t = token[0].lower()
            # Here we should be identifying the types that each token is and place it correctly
            tval = 4 # 4 is the default case
            
            # try to find the type of the token and save it to tval
            if self.verifier.isType1(t, domain):
                tval = 1
            elif self.verifier.isType2(t, domain):
                tval = 2
            elif self.verifier.isType3(t, domain):
                tval = 3
            elif isNumeric(t):
                tval = 3
            
            # Adds the token to the list
            ret.append([token[0], tval])
        return ret
    
    
def isNumeric(token) -> bool:
    pos = 0
    for c in token:
        pos += 1
        if c in string.digits or c==',' or c=='.' or (pos == len(token) and (c=='k' or c=='K')):
            continue # valid numeric character, but all need to be checked
        else:
            return False # break on first invalid
    # If all characters were valid, then we have a valid numeric token
    return True
    
