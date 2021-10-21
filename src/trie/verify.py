import string
from pathlib import Path
from . import trie
from src import domains
Domain = domains.Domain

class TypeVerifier(object):
    # Tests for type 1 words

# Members ---------------------------------------------------------------------

    def __init__(self):

        # domains specified in Domains class

        # TYPE 1 Members ------------------------------------------------------

        # Trie members
        Trie = trie.Trie
        self.carTries = [Trie()] * 3
        self.furnitureTries = [Trie()] * 3
        self.jewelryTries = [Trie()] * 3
        self.motorcycleTries = [Trie()] * 3
        self.housingTries = [Trie()] * 3
        self.csjobsTries = [Trie()] * 3


        # load dictionaries
        trieDirs = [["cars", self.carTries], ["jewelry", self.jewelryTries], ["motorcycles", self.motorcycleTries],
                   ["furniture", self.furnitureTries], ["housing", self.housingTries], ["csjobs", self.csjobsTries]]
        
        for i in range(1, 3): # there are three types
            filePath = "type" + str(i) + "words/"
            if i > 1:
                break # we actually don't have more than Type I implemented
            
            for trieDir in trieDirs:
                # We won't need the full list since the trie holds all necessary data
                typeList = self.__loadLowerLines(filePath + trieDir[0] + "-" + str(i) + ".txt")
                for word in typeList:
                    trieDir[1][i-1].insert(word.lower())
    
    
    def __loadLowerLines(self, directory: string):
        file = open(str(Path(__file__).parent) + "/../../trie/" + directory, encoding='utf-8')
        allLines = file.read()
        lines = allLines.split('\n')
        for line in lines:
            line = line.lower()
        file.close()
        return lines

# Access Functions ------------------------------------------------------------

    def isType1(self, word, domain):
        return self.__isType(word, domain, 0)

    def isType2(self, word, domain):
        return self.__isType(word, domain, 1)

    def isType3(self, word, domain):
        return self.__isType(word, domain, 2)
    
    def __isType(self, word:string, domain, typeNo: int) -> bool:
        if (domain == Domain.CAR):
            return self.carTries[typeNo].search(word)
        elif (domain == Domain.FURNITURE):
            return self.furnitureTries[typeNo].search(word)
        elif (domain == Domain.JEWELRY):
            return self.jewelryTries[typeNo].search(word)
        elif (domain == Domain.MOTORCYCLE):
            return self.motorcycleTries[typeNo].search(word)
        elif (domain == Domain.HOUSING):
            return self.housingTries[typeNo].search(word)
        elif (domain == Domain.JOB):
            return self.csjobsTries[typeNo].search(word)
        else:
            return False
