'''
Created on Oct 1, 2021

@author: moultmat
'''
from src.typify import TypeExtractor
from src.domains import Domain, getTable
from src import database
import string


def __extractOfType(typed:[[string, int]], toExtract:int) -> [string]:
    """
    Extracts all tokens in the input query that match the type specified.
    @param typed: the typed query
    @param toExtract: the type to extract. Expected in 1-indexed. For example, Type I should be 1.
    @return a list of the string tokens that match the required type
    """
    ofType = []
    for token in typed:
        if token[1] == toExtract:
            ofType.append(token[0])
    return ofType


def __matchColumns(typeValues:[string], typeCols:[int], table:database.Table) -> [[string, [int]]]:
    """
    Uses database queries to find which columns/attributes each of the typed tokens apply to.
    @param typeValues: a list of token values in the original query that were found to be the correct type
    @param typeCols: a list of columns in the table that are applicable for the used type
    @param table: the table that should be searched with the specified columns
    @return a list of token lists, where the first index in each sublist is the string token, and the second
    index is the column(s) found for that string token. For example: [['foo', [0,1]], ['bar', [1]]]
    """
    matchList = []
    for token in typeValues:
        matched = []
        for col in typeCols:
            where = table.dat[col][0] + ' LIKE "%' + token + '%"'
            #print(where)
            result = database.query(table, [col], where)
            if len(result) > 0: # If there was some match in this column
                matched.append(col)
            if len(matched) > 0:
                matchList.append([token, matched])
    return matchList


def __reduce(matchList: [[string, [int]]], table:database.Table):
    """
    Attempts to reduce the match list (as returned from __matchColumns) by combining sequential tokens of the
    same type. Calls will be made to the database to ascertain whether the combined types exist before the
    tokens are merged. Potential merging possibilities include sequential (fx 'Harley' 'Davidson' -> 'Harley Davidson')
    and reverse (fx 'Accord' 'Honda' -> 'Honda Accord')
    @param matchList: the list of tokens and attributes to try to merge
    @param table: the table to which these tokens belong
    @return none. The matchList parameter is modified.
    """
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


def type1Where(typed:[[string, int]], table:database.Table) -> [string]:
    # We are going to want to pull out all the type Is from the typed query
    typeI = __extractOfType(typed, 1)
    
    # Now we want to see which type 1 these match (if there are multiple columns for this domain)
    typeICol = table.idxCol
    
    '''
    print("Type 1 tokens:")
    print(typeI)
    print("Type 1 columns:")
    print(typeICol)
    '''
    
    # First we want to know which of the Type I columns each token matches to. There could be several.
    matchList = __matchColumns(typeI, typeICol, table)
    # And with that match list, we will try to reduce terms
    __reduce(matchList, table)
        
    # At this point, we should have a finalized matchList to operate with
    #print(matchList)
    # We are going to separate each of the different constraints (so that some may be dropped if needed in partial matching)
    ret = []
    for matched in matchList:
        ret.append(table.dat[matched[1]][0] + ' LIKE "%' + matched[0] + '%"')
    return ret


def type2Where(typed:[[string, int]], table:database.Table, domain:Domain,) -> [string]:
    typeII = __extractOfType(typed, 2)
    
    # There is nowhere else that Type II attributes are saved for each table.
    #  Thus, the data is here: 
    cols = []
    if domain == Domain.CAR:
        cols = [1, 6, 8, 10, 11, 12, 13, 14, 15, 16]
    elif domain == Domain.FURNITURE:
        cols = [8, 9]
    elif domain == Domain.HOUSING:
        cols = [0, 1, 15, 18]
    elif domain == Domain.JEWELRY:
        cols = [4, 5] # maybe the title should be considered an indexing key...
    elif domain == Domain.JOB:
        cols = [3, 5, 6, 7, 9, 10, 11, 13]
    elif domain == Domain.MOTORCYCLE:
        cols = [3]
    
    matchList = __matchColumns(typeII, cols, table)
    __reduce(matchList, table)
    
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
    print(typed, '\n')
    
    # Now we want to start building the query.
    #  It is going to be in the form of a SELECT statement, with an AND for each of the types that need to be matched
    #  For example, SELECT * FROM table WHERE typeI AND typeII AND typeIII
    typeIWhere = type1Where(typed, table)
    print(typeIWhere)
    typeIIWhere = type2Where(typed, table, domain)
    print(typeIIWhere)
    
    
