import unittest


class TestTrie(unittest.TestCase):
    '''
    Tests that the TrieVerify class is properly loading the tries for each of the domains.
    '''

    def testVerify(self):
        from . import verify
        verify = verify.TypeVerifier()

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
    
    
    def testTrie(self):
        strings = ["pqrs", "pprt", "psst", "qqrs", "pqrs"]
        
        from . import trie
        t = trie.Trie()
        for word in strings:
            t.insert(word)
        
        self.assertTrue(t.search("pqrs"), 'search could not find inserted element')
        self.assertTrue(t.search("pprt"), 'search could not find inserted element')
    
        t.delete("pprt")
        self.assertFalse(t.search("pprt"), 'search found a deleted element')
    
        t.update("mnop", "pprt")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
