from src.verify import Type1Verifier

if __name__ == '__main__':

    verify = Type1Verifier()

    # TEST:
    # domains
    domains = ["car", "furniture", "jewelry", "motorcycle", "housing", "csjobs"]

    # list of known type 1's, plus last option not a type 1
    carList = ["honda", "toyota", "notAType1"]
    furnitureList = ["stool", "desk", "notAType1"]
    jewelryList = ["bracelet", "ring", "notAType1"]
    motorcycleList = ["triumph", "honda", "notAType1"]
    housingList = ["condo", "townhouse", "notAType1"]
    csjobsList = ["engineer", "analyst", "notAType1"]

    listsByDomain = [carList, furnitureList, jewelryList, motorcycleList, housingList, csjobsList]

    for i in range(len(listsByDomain)):
        print("Domain: " + domains[i])
        for word in listsByDomain[i]:
            print("Word: " + word + ". ISTYPE1: " + str(verify.isType1(word, domains[i])))
