from src.typify import TypeExtractor, isNumeric
from src.domains import Domain, getTable
from src import database
import string

class ConstraintBuilder():
    
    def __init__(self):
        import src.multinomial_classification.run_classifier as classify
        self.classifier = classify.Classifier()
        self.extractor = TypeExtractor()
        
        # With that in place, we want to load some data from files containing boundary words
        #  and superlative words.
        # We load the file that has all the boundary synonyms
        from pathlib import Path
        synFile = open(str(Path(__file__).parent) + "/../boundary-synonyms.txt", encoding='utf-8')
        self.bounders = []
        self.applications = None
        currBound = []
        currSym = None
        for line in synFile:
            if self.applications is None:
                line = line[0:-1] # to remove the trailing new line
                if len(line) == 0:
                    if len(currBound) > 0:
                        self.bounders.append([currSym, currBound])
                        currBound = []
                    currSym = None
                else:
                    if line[0] == '-': # The dash barrier marks the end of the boundary synonyms
                        self.applications = {}
                    elif currSym is None: # the new symbol is set
                        currSym = line
                    else:
                        currBound.append(line)
            else:
                # For applications. These are definitions of parenthesized numbers (which are used by boundary synonyms)
                firstEnd = line.find(' ')
                # The first token is the application defined
                defed = line[0:firstEnd]
                # All other tokens ought to be separated by ;
                split = line[firstEnd+1:-1].split('; ')
                self.applications.update({defed: split})
        if len(currBound) > 0:
            self.bounders.append([currSym, currBound])
        synFile.close()


    def __matchWhere(self, name:string, value:string) -> string:
        return name + ' LIKE "% ' + value + ' %"'


    def __extractOfType(self, typed:[[string, int]], toExtract:int) -> [string]:
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
    
    
    def __matchColumns(self, typeValues:[string], typeCols:[int], table:database.Table) -> [[string, [int]]]:
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
                where = self.__matchWhere(table.dat[col][0], token)
                #print(where)
                result = database.query(table, [col], where)
                if len(result) > 0: # If there was some match in this column
                    matched.append(col)
            if len(matched) > 0:
                matchList.append([token, matched])
        return matchList
    
    
    def __reduce(self, matchList: [[string, [int]]], table:database.Table) -> [[[string, int]]]:
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
                ls[i].append([matched[0], col, [i]])
        
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
                        where = self.__matchWhere(table.dat[col][0], tryName)
                        if len(database.query(table, [col], where)):
                            # There was a match, therefore we need to remove both curr and last from their respective lists
                            ls[i].pop(c)
                            ls[i-1].pop(a)
                            # It is replaced by the new joint entry
                            ls[i].insert(0, [tryName, col, last[2]+curr[2]]) # insert at the beginning so we don't redo it
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
        
        # After reduction is done, the order does not matter, so we flatten ls
        # A token can only be used once, and we would like to take all the possibilities better into account, but 
        #  it may not be worth it to enumerate all interpretations of the query. Therefore, we return a simplified
        #  enumeration and leave a better solution to the reader.
        ret = []
        for pos in ls:
            orList = []
            for token in pos:
                orList.append(token)
            if len(orList) > 0:
                ret.append(orList)
        
        return ret
    
    
    def __convertToSQL(self, matchList:[[[string, int]]], table:database.Table) -> [string]:
        ret = []
        for matched in matchList:
            # Inside each match (where each are and-ed), we can have several options, where each should be or-ed
            where = ''
            for matchOr in matched:
                if len(where) > 0:
                    where += ' OR '
                where += self.__matchWhere(table.dat[matchOr[1]][0], matchOr[0])
            ret.append(where)
        return ret
    
    
    def type1Where(self, typed:[[string, int]], table:database.Table) -> [string]:
        # We are going to want to pull out all the type Is from the typed query
        typeI = self.__extractOfType(typed, 1)
        
        # Now we want to see which type 1 these match (if there are multiple columns for this domain)
        typeICol = table.idxCol
        
        '''
        print("Type 1 tokens:")
        print(typeI)
        print("Type 1 columns:")
        print(typeICol)
        '''
        
        # First we want to know which of the Type I columns each token matches to. There could be several.
        matchList = self.__matchColumns(typeI, typeICol, table)
        #print("match list:", matchList)
        # And with that match list, we will try to reduce terms
        matchList = self.__reduce(matchList, table)
            
        # At this point, we should have a finalized matchList to operate with
        #print(matchList)
        # We are going to separate each of the different constraints (so that some may be dropped if needed in partial matching)
        return self.__convertToSQL(matchList, table)
    
    
    def type2Where(self, typed:[[string, int]], table:database.Table, domain:Domain) -> [string]:
        typeII = self.__extractOfType(typed, 2)
        
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
        
        matchList = self.__matchColumns(typeII, cols, table)
        matchList = self.__reduce(matchList, table)
        return self.__convertToSQL(matchList, table)
    
    
    def __standardizeQuery(self, typed:[[string, int]]) -> [[string, int]]:
        # Go through each of the bounders and try to match them to tokens in the query
        for bounder in self.bounders:
            sym = bounder[0]
            for option in bounder[1]:
                # For each option that maps to the given symbol
                #  We will want to break each option into component tokens
                comps = option.split(' ')
                changes = True # we will cycle through the typified query tokens until no changes can be made
                while changes:
                    changes = False
                    unit = '' # the units found
                    i = 0 # the current component index to match with
                    start = -1
                    end = -1
                    for j in range(len(typed)):
                        token = typed[j]
                        reset = False
                        # we can only consider the token for boundary if it is a type 4
                        # or optionally we can have a unit if we are looking for one
                        if token[1] == 4 or (token[1] == 3 and comps[i] == '*'):
                            # Now we try to make a match
                            if comps[i] == '*':
                                if token[1] != 3 and token[0].lower() == comps[i+1]:
                                    i += 2 # match, now move on to next
                                else:
                                    # otherwise, save the unit we found
                                    if len(unit) > 0:
                                        unit += ' '
                                    unit += token[0].lower()
                            elif comps[i][0] == '(' and comps[i][-1] == ')':
                                # we found an application. This should be saved, but then skipped over
                                if len(unit) > 0:
                                    unit += ' '
                                
                                appCode = token[0].lower() # currently all app codes are numbers, but that could change
                                if appCode in self.applications:
                                    # match of application definition
                                    if len(unit) > 0:
                                        unit += ' '
                                    unit += ' '.join(self.applications[appCode])
                                i += 1 # move on, since we don't actually match against an application
                            elif comps[i] == token[0].lower(): # we need an exact match
                                i += 1 # go to the next component to match
                            else:
                                reset = True
                            
                            # Now verify that i is within correct bounds
                            if i >= len(comps):
                                # We have a complete match!
                                end = j
                                break
                        else:
                            reset = True # reset any progress since all tokens in the pattern must be consecutive
                        if reset:
                            i = 0 # reset any progress we have made
                            start = j+1 # this is potentially where the pattern begins
                    
                    # If we made it out of the token loop, we want to see if the range finished
                    if end != -1:
                        # It did. Now we make the replacement
                        value = sym
                        if len(unit) > 0:
                            value += " (" + unit + ")"
                        typed = typed[0:start] + [[value, 4]] + typed[end+1:]
                        changes = True
        
        # There are just a few different phrases for ranges:
        #  Between * (and/to/-) *
        #  From * (to/-) *
        #  * - *
        # Since the - is the common denominator in all, we will simplify to that.
        #  There should be no other cases of - by itself, since negation is without a space.
        rangeType = None
        for token in typed:
            if token[0].lower() == 'between' or token[0].lower() == 'from':
                rangeType = token[0].lower()
            
            elif rangeType is not None:
                if token[0].lower() == 'to' or (rangeType == 'between' and token[0].lower() == 'and'):
                    token[0] = '-' # transform to a simple hyphen, maintaining type
                
                # Between the range start and the range middle, we only expect to encounter number values and units.
                elif token[1] == 3:
                    continue
                # If we get anything else, break the range construct
                rangeType = None
            
        return typed
    
    
    def __isBoundOperation(self, x:string) -> bool:
        for bounder in self.bounders:
            sym = bounder[0]
            if x.find(sym) == 0 and (len(x) == len(sym) or x[len(sym)]==' '): # if the bounding symbol is the first in the string,
                return True #- then we know it is a bounding operation
        return False
    
    '''
    Partial Match for typeIII. 
    If there is no exact match for a numerical value in the certain column of the certain table,
    then return the record with the closest value to the target one.
    '''
    def partialTypeThree(self, value, table, column):
        query = f"SELECT * FROM {table} ORDER BY ABS\( {value} - {column}\) LIMIT 1"
        return database.execute(query)
    
    
    def type3Where(self, typed:[[string, int]], table:database.Table) -> [string]:
        # The first thing that we will want to do is identify boundaries and associated units
        #  Boundaries such as less than, greater than, etc.
        typed = self.__standardizeQuery(typed)
        print("bounded query: ", typed)
        
        ret = [] # a list of SQL where clauses to return
        # We will want to find the unit attached to each type 3. It can be either before or after
        black = -1 # if we use a unit after the number, the unit cannot be reused for before the next number
        for i in range(len(typed)):
            if i <= black: # skip forward if this index is already blacklisted
                continue
            
            token = typed[i]
            if token[1]==3 and isNumeric(token[0]):
                # We found a value! Now we need to find a corresponding unit.
                # Also, we should look for a bounding operation (> >= < <=)
                #  If no bounding operation is found, we assume equivalency
                
                unit = None
                bound = None
                otherVal = None # This is used only if the value is part of a range
                
                # First, try going backwards until the blacklisted.
                # We are going to try two movement directions:
                #  First, going backwards until the blacklisted.
                #  Next, going forward until the end of the query
                # If we hit an unexpected token, we abort that direction.
                
                # Last thing to mention: we need two different append operations to create joint units.
                #  Going backwards, we want it to be curr + space + last
                #  Going forward, we want to have last + space + curr
                def backAppend(last:string, curr:string) -> string:
                    return curr + ' ' + last
                def spaceAppend(last:string, curr:string) -> string:
                    return last + ' ' + curr
                
                directions = [[range(i-1, black, -1), backAppend], [range(i+1, len(typed)), spaceAppend]]
                for dirr in directions:
                    foundUnit = unit is not None
                    for j in dirr[0]:
                        if typed[j][1] == 3 and not isNumeric(typed[j][0]) and not foundUnit:
                            # We assume this is the unit. It is type 3, which is either a unit or a number.
                            #  It is not a number. Therefore, we assume it is the unit.
                            if unit is not None: # we found another unit, and we already have a unit
                                unit = dirr[1](unit, typed[j][0]) # create a joint unit by the direction's concat function
                            else:
                                unit = typed[j][0]
                        elif typed[j][1] == 4 and self.__isBoundOperation(typed[j][0]) and j<i: # we can only find bounds before
                            if bound is not None:
                                break # cannot have two bounds!
                            bound = typed[j][0]
                            if bound.find('(') != -1 and bound.find(')') != -1:
                                # the unit is inside the bound
                                start = bound.find('(')+1
                                end = bound.find(')')
                                
                                unit = bound[start:end]
                                bound = bound[0:bound.find(' ')] # cut off before the first space (which is the end of the symbol)
                            if unit is not None:
                                break # don't need to go back more if we have the bound and the unit
                        elif bound is None and typed[j][0] == '-' and j>i: # we found a range indicator (though this can only come after and with no other bound)
                            backup = j
                            # If we find a range indicator, we need to do something special. Continue and find the next value,
                            #  and if the unit has not already been specified, the next unit. These are both used to build a new bound
                            while unit is None or otherVal is None:
                                abort = False
                                j += 1
                                if j >= len(typed):
                                    abort = True
                                
                                if not abort:
                                    if typed[j][1] == 3:
                                        if isNumeric(typed[j][0]):
                                            otherVal = typed[j][0]
                                        elif unit is None: # sometimes the unit is given twice. If so, ignore
                                            unit = typed[j][0]
                                    else: # something unexpected!
                                        abort = True
                                
                                if abort:
                                    # If we are just missing the unit, we are okay
                                    if otherVal is None:
                                        # If we don't have the other value, then we have an ill-formed range
                                        # Assume we misinterpreted something, and pretend we never saw the range
                                        i = backup
                                    break
                            i = j
                            break # After range computations, we don't want to stick around looking for more
                        else:
                            break # If we found something unexpected, we stop going backwards
                        
                        # black list the token(s) that we have used so far
                        if j > i: # if we are moving forward
                            black = j
                    black = max(black, i)
                
                # Now that we have a unit, we are going to try to use it.
                #  If we don't have any unit, we try to match to year (if the table allows it)
                if unit is None:
                    unit = "year"
                if not unit is None:
                    cols = []
                    # Find whether the unit exists in the table.
                    for attr in table.dat:
                        if len(attr) == 3: # if it has length three, then it is of the form: name, type, [units]
                            # Therefore, we try to match the found unit to the unit here
                            units = attr[2]
                            for tUnit in units:
                                if tUnit == unit:
                                    # We don't have to match all the unit variations, only one
                                    cols.append(attr[0][0])
                                    break
                    # Now that we found (all) column(s) matching the unit, we want to create the relation(s) 
                    if len(cols) > 0:
                        # we found maybe several matches. They should be OR-ed together to the final result
                        # Each of the unit matches are in cols
                        
                        # Also, if we have a range, we want to sort out which value is the lower, and which is the higher
                        value = token[0]
                        if otherVal is not None:
                            if float(otherVal) < float(value):
                                value = otherVal
                                otherVal = value
                        
                        where = ''
                        for unitMatch in cols:
                            if len(where) > 0:
                                where += ' OR '
                            # We assume that the bound is in a correct form (since it is defined in a file we control).
                            #  Therefore, since SQL supports >, >=, <, and <=, we can simply use it in the where clause
                            bb = '=' # equals is the assumed bounding operation.
                            if bound is not None:
                                bb = bound
                            
                            if otherVal is None: # no range, normal path
                                where += (unitMatch + ' ' + bb + ' ' + value)
                            else:
                                where += ('(' + unitMatch + ' >= ' + value + ' AND ' + unitMatch + ' <= ' + otherVal + ')')
                        ret.append(where)
        
        return ret
    
    
    def orderBy(self, typed:[[string, int]], table:database.Table) -> string:
        return ''
    
    
    def tokenize(self, text: string) -> [string]:
        import nltk
        # first order of business is going to be to tokenize the text
        tokens = nltk.word_tokenize(text)
        # NLTK will do most of the work for us, but we need to do some extra checks for hyphens.
        #  Sometimes hyphens are used to indicate ranges (fx $200-500), but it can also be used for model names (f-150)
        #  Some words are also just hyphenated, such as community-based, meat-fed, etc.
        i = 0
        inst = -1
        while i < len(tokens):
            #print(tokens[i])
            inst = tokens[i].find('-', inst+1)
                
            if inst > -1:
                # Analyze whether this is a range, or a name
                #  We can distinguish if there is a letter on at least one side
                
                # However,'K' cannot count for the left side, since it is often an abbreviation for thousand.
                lettersButK = str(string.ascii_letters).replace('K', '')
                
                if inst > 0 and inst + 1 < len(tokens[i]) and \
                not (tokens[i][inst-1] in lettersButK or tokens[i][inst+1] in string.ascii_letters):
                    # Found an instance to separate!
                    whole = tokens[i]
                    tokens[i] = whole[0:inst]
                    tokens.insert(i+1, '-')
                    tokens.insert(i+2, whole[inst+1:])
                    i += 1 # since we want to skip the hyphen we just added
                else: # if it was not an instance to break, there may be more
                    continue # do not continue to next word (by skipping back to beginning of loop)
            inst = -1 # reset to searching whole word
            i += 1 # go to the next token 
        return tokens


    def fromQuery(self, query:string, toLog:bool):
        if toLog:
            def log(*args):
                for a in args:
                    print(a, end=' ')
                print()
        else:
            def log(*args):
                pass
        
        # Now we must categorize the query to know which domain we are searching
        log("Classifying query...")
        classified = self.classifier.classify([query])
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
        self.table = getTable(domain)
        log("Identified as:", domain.name.lower())
        
        # We want to tokenize the query
        tokens = self.tokenize(query)
        
        # and then correct any misspellings
        # To do so, we need to have a big trie with all three types of the correct domain
        log("Correcting spelling...")
        trieList = self.extractor.verifier.getDomainTries(domain)
        from src.trie.trie import Trie
        bigTrie = Trie()
        for trie in trieList:
            for word in trie.wordSet:
                bigTrie.insert(word)
        # There are also some words that are universal (not specific to domain)
        # TODO: load these from boundary-synonyms.txt and superlatives-synonyms.txt
        universalWords = set()
        for bounder in self.bounders:
            for phrase in bounder[1]:
                for word in phrase.split(' '):
                    # There are some tokens that we should not add as words, namely the
                    #  wild card (*) and applications (parenthesized application codes)
                    if not('(' in word or ')' in word or word=='*'):
                        universalWords.add(word)
        for key in self.applications.keys():
            for synonym in self.applications[key]:
                universalWords.add(synonym)
        
        for word in universalWords:
            bigTrie.insert(word)
        # There are also domain-specific words we will enter
        for attr in self.table.dat:
            for typeSynonym in attr[0]:
                bigTrie.insert(typeSynonym)
            if len(attr) > 2:
                for unit in attr[2]:
                    bigTrie.insert(unit)
        # Now we can actually perform the spelling corrections (if any)
        '''
        from src.trie.spellCorrection import SpellCorrection
        i = 0
        while i < len(tokens):
            corrector = SpellCorrection(bigTrie, tokens[i])
            print(tokens[i])
            fixed = corrector.suggestion()
            if len(fixed) > 0:
                fixed = tokens[i]
            fixed = fixed.split(' ')
            for j in range(len(fixed)):
                if j==0:
                    tokens[i] = fixed[j]
                else:
                    tokens.insert(i+j, fixed[j])
            i += 1
        '''
        
        # now we want to pull some data out (Type I, II, III)
        typed = self.extractor.typify(tokens, domain)
        log("Typed query:")
        log(typed, '\n')
        
        # Now we want to start building the query.
        #  It is going to be in the form of a SELECT statement, with an AND for each of the types that need to be matched
        #  For example, SELECT * FROM table WHERE typeI AND typeII AND typeIII
        # TODO: we don't handle any explicit boolean operators like 'or'
        typeIWhere = self.type1Where(typed, self.table)
        log(typeIWhere)
        typeIIWhere = self.type2Where(typed, self.table, domain)
        log(typeIIWhere)
        typeIIIWhere = self.type3Where(typed, self.table)
        log(typeIIIWhere)
        
        orderByClause = self.orderBy(typed, self.table)
        # We can use the LIMIT clause to limit the number of responses. Generally, we don't want more than 10 at a time
        


if __name__ == '__main__':
    # We should get a query from the user here
    # (Here is a sample query that we hardcode in for testing.)
    query = 'jewelry weeding collections $50000'
    '''Here are some other queries that we could have used:
    Fabricated examples:
    'blue Kawasaki Ninja 400 no more than 200,000 miles and above $6,000'
    'automatic toyota black car in new condition cheapest'
    'house in Australia with 2 bathrooms'
    'senior data engineer in utah'
    'apartment in Provo'
    'house in Melbourne Australia with 5 bedrooms'
    'honda accord red like new'
    'golden necklace that is 16 carat'
    'jeep wrangler between $10K-20K'
    'car with mileage between 500 and 600 mi'
    'chair from $20 to $30'
    'house or apartment with 2 - 4 rooms'
    'car with from 4-8 cylinders'
    
    Mechanical Turk queries:
    'red or green cedar and cherry nightstands for $1000 or less and at least 2" high'
    'jewelry weeding collections $50000'
    'TOYOTA MOTORCYCLE SECOND HAND $10000 BLUE COLOR  300,000 MILAGE'
    '''
    
    '''Tricky reduction queries
    'honda accord red like new haven' -> [honda] [accord] [red] (([like new] [haven]) \/ [new haven])
    'honda accord red new haven' -> [honda] [accord] [red] (([new] [haven]) \/ [new haven])
    'honda accord red like new' -> [honda] [accord] [red] ([like new] \/ [new])
    'honda accord red new' -> [honda] [accord] [red] ([new] \/ [new])
    '''
    
    cb = ConstraintBuilder()
    cb.fromQuery(query, True)
    
    # Here we will employ the partial matcher to refine our results.
    #  We will modify some of the constraints
    
    
    
