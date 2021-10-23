'''
Created on Oct 1, 2021

@author: moultmat
'''
from src.typify import TypeExtractor
from src.domains import Domain
from src.database import motorcycles, jewelry, furniture, jobs, housing, cars

if __name__ == '__main__':
    # We should get a query from the user here
    # (Here is a sample query that we hardcode in for testing.)
    query = 'Kawasaki Ninja 400 less than 200,000 miles and under $6,000'
    
    # Now we must categorize the query to know which domain we are searching
    domain = Domain.MOTORCYCLE
    
    # now we want to pull some data out (Type I, II, III)
    extractor = TypeExtractor()
    typed = extractor.typify(query, domain)
    print(typed)
    
    # We are going to want to pull out all the type Is.
    typeI = []
    for token in typed:
        if token[1] == 1:
            typeI.append(token[0])
    # Now we want to see which type 1 these match (if there are multiple columns for this domain)
    domainTypeI = {
        Domain.MOTORCYCLE: motorcycles.idxCol,
        Domain.JEWELRY: jewelry.idxCol,
        Domain.JOB: jobs.idxCol,
        Domain.FURNITURE: furniture.idxCol,
        Domain.HOUSING: housing.idxCol,
        Domain.CAR: cars.idxCol
    }
    typeICol = domainTypeI[domain]
    
    print(typeICol)
    print(typeI)
    # The next thing to do here is to try to match all the type I values to columns. Use the "like" keyword, since they may only be part of the
    #  Type I value. It is possible for both tokens to be in the same column, or all in different columns. Therefore, we will have to handle
    #  them separately. If they turn out to be in the same column, we will try to place them in a set order. For example, in "Harley Davidson",
    #  both Harley and Davidson would be in the same column, so we would see if "Harley Davidson" exists. Otherwise, it is possible that the
    #  tokens are matching in the same attribute, but on different entries.
    
    
