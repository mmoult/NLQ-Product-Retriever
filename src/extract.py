'''
Created on Oct 1, 2021

'''
import string
import nltk
from pathlib import Path

class DataExtractor(object):
    '''
    Extracts different type of data from the text
    '''

    def __init__(self):
        self.typed = []

        placeFile = open(Path(__file__).parent / "../place-names.txt")
        wholeList = placeFile.read()
        self.placeNames = wholeList.split('\n')
        for name in self.placeNames:
            name = name.lower()
        placeFile.close()

        measureFile = open(Path(__file__).parent / "../measure-units.txt")
        allMeasure = measureFile.read()
        self.measureUnits = allMeasure.split('\n')
        for name in self.measureUnits:
            name = name.lower()
        measureFile.close()

        # Read in Abbreviations below

        abbrFile = open(Path(__file__).parent / "../abbreviations/2letter-abbr/case-insensitive/i-2-car-abbr.txt")
        allCar2Abbr = abbrFile.read()
        self.car2Abbr = allCar2Abbr.split('\n')
        for name in self.car2Abbr:
            name = name.lower()
        abbrFile.close()

        # COMMENT: ok to reuse abbrFile?
        abbrFile = open(Path(__file__).parent / "../abbreviations/2letter-abbr/case-insensitive/i-2-csjobs-abbr.txt")
        allCsjobs2Abbr = abbrFile.read()
        self.csjobs2Abbr = allCsjobs2Abbr.split('\n')
        for name in self.csjobs2Abbr:
            name = name.lower()
        abbrFile.close()

        abbrFile = open(Path(__file__).parent / "../abbreviations/2letter-abbr/case-insensitive/i-2-furniture-abbr.txt")
        allFurniture2Abbr = abbrFile.read()
        self.furniture2Abbr = allFurniture2Abbr.split('\n')
        for name in self.furniture2Abbr:
            name = name.lower()
        abbrFile.close()

        abbrFile = open(Path(__file__).parent / "../abbreviations/2letter-abbr/case-insensitive/i-2-jewelry-abbr.txt")
        allJewelry2Abbr = abbrFile.read()
        self.jewelry2Abbr = allJewelry2Abbr.split('\n')
        for name in self.jewelry2Abbr:
            name = name.lower()
        abbrFile.close()

        abbrFile = open(Path(__file__).parent / "../abbreviations/2letter-abbr/case-insensitive/i-2-housing-abbr.txt")
        allHousing2Abbr = abbrFile.read()
        self.housing2Abbr = allHousing2Abbr.split('\n')
        for name in self.housing2Abbr:
            name = name.lower()
        abbrFile.close()

        abbrFile = open(Path(__file__).parent / "../abbreviations/2letter-abbr/case-insensitive/i-2-motorcycles-abbr.txt")
        allMotorcycles2Abbr = abbrFile.read()
        self.motorcycles2Abbr = allMotorcycles2Abbr.split('\n')
        for name in self.motorcycles2Abbr:
            name = name.lower()
        abbrFile.close()

        abbrFile = open(Path(__file__).parent / "../abbreviations/3letter-abbr/case-insensitive/i-3-car-abbr.txt")
        allCar3Abbr = abbrFile.read()
        self.car3Abbr = allCar3Abbr.split('\n')
        for name in self.car3Abbr:
            name = name.lower()
        abbrFile.close()

        abbrFile = open(Path(__file__).parent / "../abbreviations/3letter-abbr/case-insensitive/i-3-csjobs-abbr.txt")
        allCsjobs3Abbr = abbrFile.read()
        self.csjobs3Abbr = allCsjobs3Abbr.split('\n')
        for name in self.csjobs3Abbr:
            name = name.lower()
        abbrFile.close()

        abbrFile = open(Path(__file__).parent / "../abbreviations/3letter-abbr/case-insensitive/i-3-furniture-abbr.txt")
        allFurniture3Abbr = abbrFile.read()
        self.furniture3Abbr = allFurniture3Abbr.split('\n')
        for name in self.furniture3Abbr:
            name = name.lower()
        abbrFile.close()

        abbrFile = open(Path(__file__).parent / "../abbreviations/3letter-abbr/case-insensitive/i-3-jewelry-abbr.txt")
        allJewelry3Abbr = abbrFile.read()
        self.jewelry3Abbr = allJewelry3Abbr.split('\n')
        for name in self.jewelry3Abbr:
            name = name.lower()
        abbrFile.close()

        abbrFile = open(Path(__file__).parent / "../abbreviations/3letter-abbr/case-insensitive/i-3-housing-abbr.txt")
        allHousing3Abbr = abbrFile.read()
        self.housing3Abbr = allHousing3Abbr.split('\n')
        for name in self.housing3Abbr:
            name = name.lower()
        abbrFile.close()

        abbrFile = open(Path(__file__).parent / "../abbreviations/3letter-abbr/case-insensitive/i-3-motorcycles-abbr.txt")
        allMotorcycles3Abbr = abbrFile.read()
        self.motorcycles3Abbr = allMotorcycles3Abbr.split('\n')
        for name in self.motorcycles3Abbr:
            name = name.lower()
        abbrFile.close()

        allCar4Abbr = open(Path(__file__).parent / "../abbreviations/4letter-abbr/case-insensitive/i-4-car-abbr.txt")
        allCar4Abbr = abbrFile.read()
        self.car4Abbr = allCar4Abbr.split('\n')
        for name in self.car4Abbr:
            name = name.lower()
        abbrFile.close()

        abbrFile = open(Path(__file__).parent / "../abbreviations/4letter-abbr/case-insensitive/i-4-csjobs-abbr.txt")
        allCsjobs4Abbr = abbrFile.read()
        self.csjobs4Abbr = allCsjobs4Abbr.split('\n')
        for name in self.csjobs4Abbr:
            name = name.lower()
        abbrFile.close()

        abbrFile = open(Path(__file__).parent / "../abbreviations/4letter-abbr/case-insensitive/i-4-furniture-abbr.txt")
        allFurniture4Abbr = abbrFile.read()
        self.furniture4Abbr = allFurniture4Abbr.split('\n')
        for name in self.furniture4Abbr:
            name = name.lower()
        abbrFile.close()

        abbrFile = open(Path(__file__).parent / "../abbreviations/4letter-abbr/case-insensitive/i-4-jewelry-abbr.txt")
        allJewelry4Abbr = abbrFile.read()
        self.jewelry4Abbr = allJewelry4Abbr.split('\n')
        for name in self.jewelry4Abbr:
            name = name.lower()
        abbrFile.close()

        abbrFile = open(Path(__file__).parent / "../abbreviations/4letter-abbr/case-insensitive/i-4-housing-abbr.txt")
        allHousing4Abbr = abbrFile.read()
        self.housing4Abbr = allHousing4Abbr.split('\n')
        for name in self.housing4Abbr:
            name = name.lower()
        abbrFile.close()

        abbrFile = open(Path(__file__).parent / "../abbreviations/4letter-abbr/case-insensitive/i-4-motorcycles-abbr.txt")
        allHousing4Abbr = abbrFile.read()
        self.housing4Abbr = allHousing4Abbr.split('\n')
        for name in self.housing4Abbr:
            name = name.lower()
        abbrFile.close()


    def classify(self, text: string, category : string):
        # running the Stanford POS Tagger from NLTK
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
            # TODO here


    def userTag(self, queryFile: string):
        queryF = open(queryFile)

        fileMode = 'a'
        outputs = [['CAR', open(Path(__file__).parent / "../tagging/car.csv", fileMode)],
                   ['JOB', open(Path(__file__).parent / "../tagging/job.csv", fileMode)],
                   ['FURNITURE', open(Path(__file__).parent / "../tagging/furniture.csv", fileMode)],
                   ['HOUS', open(Path(__file__).parent / "../tagging/housing.csv", fileMode)],
                   ['JEWELRY', open(Path(__file__).parent / "../tagging/jewelry.csv", fileMode)],
                   ['CYCLE', open(Path(__file__).parent / "../tagging/motorcycle.csv", fileMode)]]
        output = None

        def normalize(b: bool) -> int:
            if b:
                return 1
            else:
                return 0

        for line in queryF:
            if not line:
                continue
            if line[0] == '=': # new output type
                for outputType in outputs:
                    if outputType[0] in line:
                        output = outputType[1]
                        break
                continue

            print("In '" + line[0:-1] + "':")
            tokens = nltk.word_tokenize(line)
            pos_tagged = nltk.pos_tag(tokens)

            ariadne = False
            for token in pos_tagged:
                ok = False
                while not ok:
                    text = input(token[0]+"= ")                                     # COMMENT: text is '1=' now, right?
                    if text == '1' or text == '2' or text == '3' or text == '4':    # COMMENT: won't this never be true?
                        ok = True
                    if not text:
                        ariadne = True
                        break
                if ariadne:
                    break
                if output != None:
                    print(text, text, normalize(self.__isPlural(token)), normalize(self.__isCapital(token)), normalize(self.__isAdjective(token)),
                                normalize(self.__isMeasurement(token)), normalize(self.__isAlphaNumeric(token)), normalize(self.__isLocation(token)),
                                normalize(self.__isAcronym(token)), sep=', ', file=output)
            if ariadne:
                break
        queryF.close()
        for outputType in outputs:
            outputType[1].close()


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
        return alpha and numeric                                                                    # COMMENT: shouldn't be alpha OR numeric?

    def __isLocation(self, token) -> bool:
        # https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population
        return token[0].lower() in self.placeNames

    def __isAcronym(self, token) -> bool:
        # TODO come back to this with common abbreviations for the different categories
        size = len(token[0])
        domain = # how do we access the domain?
        return token[0].lower() in self.getAbbr(size, domain)

    def getAbbr(self, size, domain):
        match size:
            case 1:
                return string.ascii_lowercase
            case 2:               #COMMENT: single letter abbreviations?
                if (domain == "cars"):
                    return self.car2Abbr
                elif (domain == "csjobs"):
                    return self.csjobs2Abbr
                elif (domain == "furniture"):
                    return self.furniture2Abbr
                elif (domain == "housing"):
                    return self.housing2Abbr
                elif (domain == "jewelry"):
                    return self.jewelry2Abbr
                elif (domain == "motorcycles"):
                    return self.motorcycles2Abbr
                else:
                    return # COMMENT: need empty array???
            case 3:
                if (domain == "cars"):
                    return self.car3Abbr
                elif (domain == "csjobs"):
                    return self.csjobs3Abbr
                elif (domain == "furniture"):
                    return self.furniture3Abbr
                elif (domain == "housing"):
                    return self.housing3Abbr
                elif (domain == "jewelry"):
                    return self.jewelry3Abbr
                elif (domain == "motorcycles"):
                    return self.motorcycles3Abbr
                else:
                    return #empty array???
            case 4:
                if (domain == "cars"):
                    return self.car4Abbr
                elif (domain == "csjobs"):
                    return self.csjobs4Abbr
                elif (domain == "furniture"):
                    return self.furniture4Abbr
                elif (domain == "housing"):
                    return self.housing4Abbr
                elif (domain == "jewelry"):
                    return self.jewelry4Abbr
                elif (domain == "motorcycles"):
                    return self.motorcycles4Abbr
                else:
                    return #empty array???
            case _:
                return

