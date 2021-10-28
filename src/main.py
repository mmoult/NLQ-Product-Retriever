from src.typify import TypeExtractor, isNumeric
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


def __reduce(matchList: [[string, int]], table:database.Table) -> [[string, int]]:
    """
    Attempts to reduce the match list (as returned from __matchColumns) by combining sequential tokens of the
    same type. Calls will be made to the database to ascertain whether the combined types exist before the
    tokens are merged. Potential merging possibilities include sequential (fx 'Harley' 'Davidson' -> 'Harley Davidson')
    and reverse (fx 'Accord' 'Honda' -> 'Honda Accord')
    @param matchList: the list of tokens and attributes to try to merge
    @param table: the table to which these tokens belong
    @return none. The matchList parameter is modified.
    """
    
    # When we get the matchList, it is a list of tokens and the column(s) that it applies to.
    #  For example: [['honda', [0]], ['accord', [0,1]]
    #  The order is important, since tokens are only logically connected to tokens in sequential order.
    #  (we would not want to try to connect tokens separated by another token). This structure given
    #  works well for simple uses. However, when we want to reduce the terms, it is possible for two
    #  tokens to require the same position. For example, if honda and accord are combined, then there
    #  must be ['honda accord', [0]] and ['accord', [1]] at the *same position* if either or both need
    #  to combine with a subsequent token.
    # Therefore, we simplify the given structure to only have one possible row and create a list for
    #  each possible position
    
    # ls is where we will save all the positional tokens. It must be the length of the original match list
    ls = []
    for _ in range(len(matchList)):
        ls.append([])
    # Now we break each token into all its rows and put it in its place
    for i in range(len(matchList)):
        matched = matchList[i]
        for col in matched[1]:
            ls[i].append([matched[0], col])
    
    # With our new structure, we want to go through each index (starting at 1) to the end and try to match
    #  with the index immediately before if the columns match
    i = 1
    while i < len(matchList):
        c = 0
        while c < len(ls[i]):
            curr = ls[i][c]
            a = 0
            while a < len(ls[i-1]):
                last = ls[i-1][a]
                # Verify that the cols of curr and last match
                if curr[1] != last[1]:
                    a += 1
                    continue
                col = curr[1]
                
                # We will try to combine sequentially, then backwards
                ariadne = False
                tryNames = [(matchList[i-1][0] + ' ' + matchList[i][0]),
                            (matchList[i][0] + ' ' + matchList[i-1][0])]
                for tryName in tryNames:
                    # The form 'column LIKE "%token%"' will match any entry where the column contains the substring "token". 
                    where = table.dat[col][0] + ' LIKE "%' + tryName + '%"'
                    if len(database.query(table, [col], where)):
                        # There was a match, therefore we need to remove both curr and last from their respective lists
                        ls[i].pop(c)
                        ls[i-1].pop(a)
                        # It is replaced by the new joint entry
                        ls[i].insert(0, [tryName, col]) # insert at the beginning so we don't redo it
                        # We only use the first combination that succeeds for this pair
                        # redo the index for a since we deleted what was there
                        # get the next index c
                        ariadne = True
                        break
                if ariadne:
                    break
                a += 1
            c += 1
        i += 1
    
    # After reduction is done, the order does not matter, so we flatten ls and return the result
    ret = []
    for pos in ls:
        for token in pos:
            ret.append(token)
    return ret


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
    #print("match list:", matchList)
    # And with that match list, we will try to reduce terms
    matchList = __reduce(matchList, table)
        
    # At this point, we should have a finalized matchList to operate with
    #print(matchList)
    # We are going to separate each of the different constraints (so that some may be dropped if needed in partial matching)
    ret = []
    for matched in matchList:
        ret.append(table.dat[matched[1]][0] + ' LIKE "%' + matched[0] + '%"')
    return ret


def type2Where(typed:[[string, int]], table:database.Table, domain:Domain) -> [string]:
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
    matchList = __reduce(matchList, table)
    
    ret = []
    for matched in matchList:
        ret.append(table.dat[matched[1]][0] + ' LIKE "%' + matched[0] + '%"')
    return ret


def type3Where(typed:[[string, int]], table:database.Table) -> [string]:
    # We will want to find the unit attached to each type 3. It can be either before or after
    #TODO: ranges have implied units. For example "300 - 500 miles" -> "300 miles" - "500 miles"
    black = -1 # if we use a unit after the number, the unit cannot be reused for before the next number
    for i in range(len(typed)):
        token = typed[i]
        if token[1]==3 and isNumeric(token[0]):
            # We found a value! Now we need to find a corresponding unit.
            #  Try the previous token
            unit = None
            if i-1!=black and typed[i-1][1] == 3 and not isNumeric(typed[i-1][0]):
                # We assume this is the unit. It is type 3, which is either a unit or a number.
                #  It is not a number. Therefore, we assume it is the unit.
                unit = typed[i-1][0]
            elif i+1 < len(typed) and typed[i+1][1] == 3 and not isNumeric(typed[i-1][0]):
                # Since we are using a unit after the number, we must set this unit to the blacklist.
                #  That way it cannot be used again by later numbers (using it as previous)
                black = i+1
                unit = typed[i+1][0]
            
            if not unit is None:
                cols = []
                # Now that we have a unit, we are going to try to use it. Hopefully it actually exists in the table
                for attr in table.dat:
                    if len(attr) == 3: # if it has length three, then it is of the form: name, type, [units]
                        # Therefore, we try to match the found unit to the unit here
                        units = attr[2]
                        for tUnit in units:
                            if tUnit == unit:
                                # We don't have to match all the unit variations, only one
                                cols.append(attr[0])
                if len(cols) > 0:
                    # we found maybe several matches. They should be OR-ed together to the final result
                    pass
    
    return [] #TODO: this is just a filler until we can get it done
    

if __name__ == '__main__':
    # We should get a query from the user here
    # (Here is a sample query that we hardcode in for testing.)
    ''' Failed queries:
    'house in Melbourne Australia with 5 bedrooms'
    'senior data engineer in utah'
    'apartment in Provo'
    'house in Australia with 2 bathrooms'
    'toyota black car in excellent condition cheapest'
    '''
    query = 'honda accord red new'
    #'Kawasaki Ninja 400 less than 200,000 miles and under $6,000'
    #'golden necklace that is 16 carat'
    
    # Now we must categorize the query to know which domain we are searching
    import src.multinomial_classification.run_classifier as classify
    classifier = classify.Classifier()
    classified = classifier.classify([query])
    if len(classified) == 0:
        raise Exception("The query could not be classified!")
    classified = classified[0]
    if classified == "car":
        domain = Domain.CAR
    elif classified == "furniture":
        domain = Domain.FURNITURE
    elif classified == "housing":
        domain = Domain.HOUSING
    elif classified == "jewelry":
        domain = Domain.JEWELRY
    elif classified == "computer science jobs":
        domain = Domain.JOB
    elif classified == "motorcycles":
        domain = Domain.MOTORCYCLE
    else:
        raise Exception("The classification of the query did not match any of the expected domains! Got: " + classified)
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
    
    
