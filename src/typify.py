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


    def typify(self, text: [string], domain) -> [[string, int]]:
        # running the Stanford POS Tagger from NLTK
        ''' Needed NLTK downloads to run:
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        '''
        
        # we also need to analyze the part of speech for each token
        pos_tagged = nltk.pos_tag(text)

        # each token will be compared with the trie structure created in the constructor
        ret = []
        i = 0
        while i < len(pos_tagged):
            token = pos_tagged[i]
            t = token[0].lower()
            original = t
            # Here we should be identifying the types that each token is and place it correctly
            tval = 4 # 4 is the default case
            
            # try to find the type of the token and save it to tval
            # The token may need to be combined with the next token to qualify for a type
            search = [1, 2, 3]
            first = True
            j = i
            while len(search) > 0 and tval == 4:
                if first:
                    first = False
                    if isNumeric(t):
                        t = toCleanNumber(t)
                        tval = 3
                        break
                elif j < len(pos_tagged) - 1:
                    j += 1
                    # try to add the next token on
                    t = t + ' ' + pos_tagged[j][0].lower()
                else:
                    # there is no next token to append
                    search.clear()
                    tval = 4
                    break
                
                toRemove = []
                for typeNum in search:
                    res = self.verifier.inType(t, domain, typeNum)
                    # Now we need to analyze the result. If it is none, we know this is not it. 
                    #  If it is terminated, then we know this token is of that type independently.
                    #  The third option is not terminated, which means we will try to append the next token and see if they go together
                    if res is None:
                        toRemove.append(typeNum)
                    elif res.terminating: # We found that this was valid for this type
                        tval = typeNum
                        i = j # update i to how far we used
                        break
                    # Otherwise, we know that the token was partially in the trie. We will try appending the next token next round
                for typeNum in toRemove:
                    search.remove(typeNum)
            
            if len(search) == 0:
                t = original # Reset the token to the original if we did not find anything
            ret.append([t, tval])
            i += 1
        return ret


def isNumeric(token) -> bool:
    pos = 0
    notPunct = False
    for c in token:
        pos += 1
        if c in string.digits:
            notPunct = True
            continue # valid numeric character, but all need to be checked
        elif c==',' or c=='.' or (pos == len(token) and (c=='k' or c=='K')):
            continue
        else:
            return False # break on first invalid
    # If all characters were valid, then we have a valid numeric token
    return notPunct and True


def toCleanNumber(x:string) -> string:
    ret = ''
    for c in x:
        if c in string.digits or c=='.':
            ret += c
        elif c=='k' or c=='K':
            ret += '000' # since k denotes a thousand
    return ret
    
