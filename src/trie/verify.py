import string
from pathlib import Path
from . import trie

class Type1Verifier(object):
    # Tests for type 1 words

# Members ---------------------------------------------------------------------

    def __loadLowerLines(self, directory: string):
        file = open(str(Path(__file__).parent) + "/../../trie/" + directory, encoding='utf-8')
        allLines = file.read()
        lines = allLines.split('\n')
        for line in lines:
            line = line.lower()
        file.close()
        return lines

    def __init__(self):

        # self.domains = ["cars", "csjobs", "furniture", "housing", "jewelry", "motorcycles"]

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

# Access Functions ------------------------------------------------------------

    def isType1(self, word, domain):
        return self.__isType(word, domain, 0)

    def isType2(self, word, domain):
        return self.__isType(word, domain, 1)

    def isType3(self, word, domain):
        return self.__isType(word, domain, 2)
    
    def __isType(self, word:string, domain:string, typeNo: int) -> bool:
        if (domain == "car"):
            return self.carTries[typeNo].search(word)
        elif (domain == "furniture"):
            return self.furnitureTries[typeNo].search(word)
        elif (domain == "jewelry"):
            return self.jewelryTries[typeNo].search(word)
        elif (domain == "motorcycle"):
            return self.motorcycleTries[typeNo].search(word)
        elif (domain == "housing"):
            return self.housingTries[typeNo].search(word)
        elif (domain == "csjobs"):
            return self.csjobsTries[typeNo].search(word)
        else:
            return False
