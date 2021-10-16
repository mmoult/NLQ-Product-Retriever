'''
Created on Oct 1, 2021

@author: moultmat
'''
from src.typify import TypeExtractor

if __name__ == '__main__':
    # here is a sample query. We would have already classified its category by now
    query = 'honda mini sedan less than 200,000 miles and under $15,000'
    
    # now we want to pull some data out (Type I, II, III)
    extractor = TypeExtractor()
    print(extractor.typify(query, "cars"))
    
