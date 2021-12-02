import string

class Mapper(object):

    def __init__(self):
        self.dictByRow = dict()
        self.dictByColumn = dict()

        print("in init")

    def constructMapFile(self):

        print("in construct file")

        # used only when .py is run standalone
        # builds files used to initialize the map

        rowsFolder = '../row_excl/'
        columnsFolder = '../column_excl/'

        files = ['cars.txt', 'csjobs.txt', 'furniture.txt', 'housing.txt',
                'jewelry.txt', 'motorcycles.txt']

        for value in files:
            print("begin row construction")
            self.constructDict(rowsFolder + value, self.dictByRow)
            print("begin column construction")
            self.constructDict(columnsFolder + value, self.dictByColumn)

        print("writing row map")
        self.writeDict(self.dictByRow, True)
        print("writing column map")
        self.writeDict(self.dictByColumn, False)

        print("end mapFile construction")

    def writeDict(self, word_dict, isRow):
        print("in write dict")

        mapFile = ''

        if isRow:
            mapFile = '../row_dict.txt'
        else:
            mapFile = '../column_dict.txt'


        with open(mapFile, 'a') as writer:
            for key in word_dict:
                writer.write(key + ' ')

                for word in word_dict[key]:
                    writer.write(word + ' ')

                writer.write('\n')



    def constructDict(self, pathname, word_dict):
        print("in constructDict")

        rows = []

        with open(pathname, 'r') as reader:
            rows = reader.readlines()

        for row in rows:
            words = row.split()

            for i in range(len(words)):
                word_i = words[i].lower()
                if word_i not in word_dict:
                    word_dict[word_i] = set()

                for k in range(len(words)):
                    word_k = words[k].lower()
                    word_dict[word_i].add(word_k)

        print("end constructDict")

        return word_dict

    # def build(self, filepath):
    # def getMap(self):

if __name__ == '__main__':
    # construct a map file

    mapper = Mapper()
    mapper.constructMapFile()
    print("exited mapper")

