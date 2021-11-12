import string
from pathlib import Path
from src.trie.trie import Trie
from src import domains
Domain = domains.Domain

class TypeVerifier(object):
    # Tests for type 1 words

# Members ---------------------------------------------------------------------

    def __init__(self):

        # domains specified in Domains class

        # TYPE 1 Members ------------------------------------------------------

        # Trie members
        self.carTries = [Trie(), Trie(), Trie()]
        self.furnitureTries = [Trie(), Trie(), Trie()]
        self.jewelryTries = [Trie(), Trie(), Trie()]
        self.motorcycleTries = [Trie(), Trie(), Trie()]
        self.housingTries = [Trie(), Trie(), Trie()]
        self.csjobsTries = [Trie(), Trie(), Trie()]


        # load dictionaries
        trieDirs = [["cars", self.carTries], ["jewelry", self.jewelryTries], ["motorcycles", self.motorcycleTries],
                   ["furniture", self.furnitureTries], ["housing", self.housingTries], ["csjobs", self.csjobsTries]]
        
        for i in range(1, 4): # there are three types
            filePath = "type" + str(i) + "words/"
            
            for trieDir in trieDirs:
                # We won't need the full list since the trie holds all necessary data
                #print(filePath + trieDir[0] + "-" + str(i) + ".txt")
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
        inDomain = self.getDomainTries(domain)
        if len(inDomain) > typeNo:
            return inDomain[typeNo].search(word)
        else:
            return False
    
    
    def getDomainTries(self, domain: Domain) -> [Trie]:
        if (domain == Domain.CAR):
            return self.carTries
        elif (domain == Domain.FURNITURE):
            return self.furnitureTries
        elif (domain == Domain.JEWELRY):
            return self.jewelryTries
        elif (domain == Domain.MOTORCYCLE):
            return self.motorcycleTries
        elif (domain == Domain.HOUSING):
            return self.housingTries
        elif (domain == Domain.JOB):
            return self.csjobsTries
        else:
            return []
