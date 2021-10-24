'''
Created on Oct 1, 2021

@author: moultmat
'''
from src.typify import TypeExtractor
from src.domains import Domain, getTable
from src import database
import string


def type1Where(typed, table:database.Table) -> [string]:
    # We are going to want to pull out all the type Is from the typed query
    typeI = []
    for token in typed:
        if token[1] == 1:
            typeI.append(token[0])
    
    # Now we want to see which type 1 these match (if there are multiple columns for this domain)
    typeICol = table.idxCol
    
    '''
    print("Type 1 tokens:")
    print(typeI)
    print("Type 1 columns:")
    print(typeICol)
    '''
    
    # First we want to know which of the Type I columns each token matches to. There could be several.
    matchList = []
    for token in typeI:
        matched = []
        for col in typeICol:
            where = table.dat[col][0] + ' LIKE "%' + token + '%"'
            #print(where)
            result = database.query(table, [col], where)
            if len(result) > 0: # If there was some match in this column
                matched.append(col)
            if len(matched) > 0:
                matchList.append([token, matched])
    # And with that match list, we will try to reduce terms
    i = 1
    while i < len(matchList):
        # If the columns for the last contains the column for this, then we can try to combine
        lastCols = matchList[i-1][1]
        matchLast = -1
        for col in matchList[i][1]:
            if col in lastCols:
                matchLast = col
                # Breaking on the first occurrence is perhaps faulty, because it assumes the first occurrence is the best.
                #  However, I don't think there will be many (if any) instances of multiple column matches. 
                break
        # The types matched in column matchLast
        if matchLast != -1:
            # We will try to combine sequentially, then backwards
            tryNames = [(matchList[i-1][0] + ' ' + matchList[i][0]),
                        (matchList[i][0] + ' ' + matchList[i-1][0])]
            for tryName in tryNames:
                # The form 'column LIKE "%token%"' will match any entry where the column contains the substring "token". 
                where = table.dat[matchLast][0] + ' LIKE "%' + tryName + '%"'
                if len(database.query(table, [matchLast], where)):
                    matchList[i-1] = [tryName, matchLast]
                    matchList.pop(i)
                    i -= 1 # redo this index since we deleted at i
                    break
            # If there was no combination, then continue in the search as normal
        i += 1
        
    # At this point, we should have a finalized matchList to operate with
    #print(matchList)
    # We are going to separate each of the different constraints (so that some may be dropped if needed in partial matching)
    ret = []
    for matched in matchList:
        ret.append(table.dat[matched[1]][0] + ' LIKE "%' + matched[0] + '%"')
    return ret
    

if __name__ == '__main__':
    # We should get a query from the user here
    # (Here is a sample query that we hardcode in for testing.)
    query = 'Kawasaki Ninja 400 less than 200,000 miles and under $6,000'
    
    # Now we must categorize the query to know which domain we are searching
    domain = Domain.MOTORCYCLE
    table = getTable(domain)
    
    # now we want to pull some data out (Type I, II, III)
    extractor = TypeExtractor()
    typed = extractor.typify(query, domain)
    print("Typed query:")
    print(typed)
    
    # Now we want to start building the query.
    #  It is going to be in the form of a SELECT statement, with an AND for each of the types that need to be matched
    #  For example, SELECT * FROM table WHERE typeI AND typeII AND typeIII
    typeIWhere = type1Where(typed, table)
    print(typeIWhere)
    
    
