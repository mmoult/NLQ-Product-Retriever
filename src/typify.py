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
        # NLTK will do most of the work for us, but we need to do some extra checks for hyphens.
        #  Sometimes hyphens are used to indicate ranges (fx $200-500), but it can also be used for model names (f-150)
        #  Some words are also just hyphenated, such as community-based, meat-fed, etc.
        i = 0
        inst = 0
        while i < len(tokens):
            #print(tokens[i])
            inst = tokens[i].find('-', inst)
                
            if inst > -1:
                # Analyze whether this is a range, or a name
                #  We can distinguish if there is a letter on at least one side
                
                # However,'K' cannot count for the left side, since it is often an abbreviation for thousand.
                lettersButK = str(string.ascii_letters).replace('K', '')
                
                if inst > 0 and inst + 1 < len(tokens[i]) and \
                not (tokens[i][inst-1] in lettersButK or tokens[i][inst+1] in string.ascii_letters):
                    # Found an instance to separate!
                    whole = tokens[i]
                    tokens[i] = whole[0:inst]
                    tokens.insert(i+1, '-')
                    tokens.insert(i+2, whole[inst+1:])
                    i += 1 # since we want to skip the hyphen we just added
                else: # if it was not an instance to break, there may be more
                    continue # do not continue to next word (by skipping back to beginning of loop)
            inst = 0 # reset to searching whole word
            i += 1 # go to the next token
        
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
                t = toCleanNumber(t)
                tval = 3
            
            # Adds the token to the list
            ret.append([t, tval])
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


def toCleanNumber(x:string) -> string:
    ret = ''
    for c in x:
        if c in string.digits or c=='.':
            ret += c
        elif c=='k' or c=='K':
            ret += '000' # since k denotes a thousand
    return ret
    
