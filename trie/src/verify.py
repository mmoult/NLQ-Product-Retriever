import string
from pathlib import Path
from src.trie import Trie

class Type1Verifier(object):
    # Tests for type 1 words

# Members ---------------------------------------------------------------------

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

        # TYPE 1 Members ------------------------------------------------------

        # domain dictionaries
        self.carType1 = []
        self.furnitureType1 = []
        self.jewelryType1 = []
        self.motorcycleType1 = []
        self.housingType1 = []
        self.csjobsType1 = []

        # Trie1 members
        self.carTrie1 = Trie()
        self.furnitureTrie1 = Trie()
        self.jewelryTrie1 = Trie()
        self.motorcycleTrie1 = Trie()
        self.housingTrie1 = Trie()
        self.csjobsTrie1 = Trie()


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

        # populate Trie1 members
        for word in self.carType1:
            self.carTrie1.insert(word.lower())

        for word in self.furnitureType1:
            self.furnitureTrie1.insert(word.lower())

        for word in self.jewelryType1:
            self.jewelryTrie1.insert(word.lower())

        for word in self.motorcycleType1:
            self.motorcycleTrie1.insert(word.lower())

        for word in self.housingType1:
            self.housingTrie1.insert(word.lower())

        for word in self.csjobsType1:
            self.csjobsTrie1.insert(word.lower())

        # TYPE 2 Members ------------------------------------------------------

        # domain dictionaries
        self.carType2 = []
        self.furnitureType2 = []
        self.jewelryType2 = []
        self.motorcycleType2 = []
        self.housingType2 = []
        self.csjobsType2 = []

        # Trie2 members
        self.carTrie2 = Trie()
        self.furnitureTrie2 = Trie()
        self.jewelryTrie2 = Trie()
        self.motorcycleTrie2 = Trie()
        self.housingTrie2 = Trie()
        self.csjobsTrie2 = Trie()


        # load dictionaries
        filePath = "type2words/"

        carFile = filePath + "cars-2.txt"
        self.carType2 = self.__loadLowerLines(carFile);

        carFile = filePath + "jewelry-2.txt"
        self.jewelryType2 = self.__loadLowerLines(carFile);

        carFile = filePath + "motorcycles-2.txt"
        self.motorcycleType2 = self.__loadLowerLines(carFile);

        carFile = filePath + "furniture-2.txt"
        self.furnitureType2 = self.__loadLowerLines(carFile);

        carFile = filePath + "housing-2.txt"
        self.housingType2 = self.__loadLowerLines(carFile);

        carFile = filePath + "csjobs-2.txt"
        self.csjobsType2 = self.__loadLowerLines(carFile);

        # populate Trie2 members
        for word in self.carType2:
            self.carTrie2.insert(word.lower())

        for word in self.furnitureType2:
            self.furnitureTrie2.insert(word.lower())

        for word in self.jewelryType2:
            self.jewelryTrie2.insert(word.lower())

        for word in self.motorcycleType2:
            self.motorcycleTrie2.insert(word.lower())

        for word in self.housingType2:
            self.housingTrie2.insert(word.lower())

        for word in self.csjobsType2:
            self.csjobsTrie2.insert(word.lower())

        # TYPE 2 Members ------------------------------------------------------

        # domain dictionaries
        self.carType3 = []
        self.furnitureType3 = []
        self.jewelryType3 = []
        self.motorcycleType3 = []
        self.housingType3 = []
        self.csjobsType3 = []

        # Trie3 members
        self.carTrie3 = Trie()
        self.furnitureTrie3 = Trie()
        self.jewelryTrie3 = Trie()
        self.motorcycleTrie3 = Trie()
        self.housingTrie3 = Trie()
        self.csjobsTrie3 = Trie()

        # load dictionaries
        filePath = "type3words/"

        carFile = filePath + "cars-3.txt"
        self.carType3 = self.__loadLowerLines(carFile);

        carFile = filePath + "jewelry-3.txt"
        self.jewelryType3 = self.__loadLowerLines(carFile);

        carFile = filePath + "motorcycles-3.txt"
        self.motorcycleType3 = self.__loadLowerLines(carFile);

        carFile = filePath + "furniture-3.txt"
        self.furnitureType3 = self.__loadLowerLines(carFile);

        carFile = filePath + "housing-3.txt"
        self.housingType3 = self.__loadLowerLines(carFile);

        carFile = filePath + "csjobs-3.txt"
        self.csjobsType3 = self.__loadLowerLines(carFile);

        # populate Trie3 members
        for word in self.carType3:
            self.carTrie3.insert(word.lower())

        for word in self.furnitureType3:
            self.furnitureTrie3.insert(word.lower())

        for word in self.jewelryType3:
            self.jewelryTrie3.insert(word.lower())

        for word in self.motorcycleType3:
            self.motorcycleTrie3.insert(word.lower())

        for word in self.housingType3:
            self.housingTrie3.insert(word.lower())

        for word in self.csjobsType3:
            self.csjobsTrie3.insert(word.lower())


# Access Functions ------------------------------------------------------------


    def isType1(self, word, domain):
        if (domain == "car"):
            return self.carTrie1.search(word)
        elif (domain == "furniture"):
            return self.furnitureTrie1.search(word)
        elif (domain == "jewelry"):
            return self.jewelryTrie1.search(word)
        elif (domain == "motorcycle"):
            return self.motorcycleTrie1.search(word)
        elif (domain == "housing"):
            return self.housingTrie1.search(word)
        elif (domain == "csjobs"):
            return self.csjobsTrie1.search(word)
        else:
            return False

    def isType2(self, word, domain):
        if (domain == "car"):
            return self.carTrie2.search(word)
        elif (domain == "furniture"):
            return self.furnitureTrie2.search(word)
        elif (domain == "jewelry"):
            return self.jewelryTrie2.search(word)
        elif (domain == "motorcycle"):
            return self.motorcycleTrie2.search(word)
        elif (domain == "housing"):
            return self.housingTrie2.search(word)
        elif (domain == "csjobs"):
            return self.csjobsTrie2.search(word)
        else:
            return False

    def isType3(self, word, domain):
        if (domain == "car"):
            return self.carTrie3.search(word)
        elif (domain == "furniture"):
            return self.furnitureTrie3.search(word)
        elif (domain == "jewelry"):
            return self.jewelryTrie3.search(word)
        elif (domain == "motorcycle"):
            return self.motorcycleTrie3.search(word)
        elif (domain == "housing"):
            return self.housingTrie3.search(word)
        elif (domain == "csjobs"):
            return self.csjobsTrie3.search(word)
        else:
            return False
