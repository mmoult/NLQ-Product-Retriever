import string
from pathlib import Path
from src.trie import Trie

class Type1Verifier(object):
    # Tests for type 1 words

    def __loadLowerLines(self, directory: string):
        file = open(str(Path(__file__).parent) + "/" + directory)
        allLines = file.read()
        lines = allLines.split('\n')
        for line in lines:
            line = line.lower()
        file.close()
        return lines

    def __init__(self):

        # self.domains = ["cars", "csjobs", "furniture", "housing", "jewelry", "motorcycles"]

        # domain dictionaries
        self.carType1 = []
        self.furnitureType1 = []
        self.jewelryType1 = []
        self.motorcycleType1 = []
        self.housingType1 = []
        self.csjobsType1 = []

        # Trie members
        self.carTrie = Trie()
        self.furnitureTrie = Trie()
        self.jewelryTrie = Trie()
        self.motorcycleTrie = Trie()
        self.housingTrie = Trie()
        self.csjobsTrie = Trie()


        # load dictionaries
        filePath = "type1words/"

        carFile = filePath + "cars-1.txt"
        self.carType1 = self.__loadLowerLines(carFile);

        carFile = filePath + "jewelry-1.txt"
        self.jewelryType1 = self.__loadLowerLines(carFile);

        carFile = filePath + "motorcycles-1.txt"
        self.motorcycleType1 = self.__loadLowerLines(carFile);

        carFile = filePath + "furniture-1.txt"
        self.furnitureType1 = self.__loadLowerLines(carFile);

        carFile = filePath + "housing-1.txt"
        self.housingType1 = self.__loadLowerLines(carFile);

        carFile = filePath + "csjobs-1.txt"
        self.csjobsType1 = self.__loadLowerLines(carFile);

        # populate Trie members
        for word in self.carType1:
            self.carTrie.insert(word.lower())

        for word in self.furnitureType1:
            self.furnitureTrie.insert(word.lower())

        for word in self.jewelryType1:
            self.jewelryTrie.insert(word.lower())

        for word in self.motorcycleType1:
            self.motorcycleTrie.insert(word.lower())

        for word in self.housingType1:
            self.housingTrie.insert(word.lower())

        for word in self.csjobsType1:
            self.csjobsTrie.insert(word.lower())

    def isType1(self, word, domain):
        if (domain == "car"):
            return self.carTrie.search(word)
        elif (domain == "furniture"):
            return self.furnitureTrie.search(word)
        elif (domain == "jewelry"):
            return self.jewelryTrie.search(word)
        elif (domain == "motorcycle"):
            return self.motorcycleTrie.search(word)
        elif (domain == "housing"):
            return self.housingTrie.search(word)
        elif (domain == "csjobs"):
            return self.csjobsTrie.search(word)
        else:
            return False
