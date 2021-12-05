from src.typify import TypeExtractor, isNumeric
from src.domains import Domain, getTable
from src import database
from src.partial import PartialMatcher
from src.opeval import OperatorHandler, OperatorEvaluator, OperatorRelation, OrRelation, AndRelation, NotRelation
import string
from src.standard import Standardizer

class ConstraintBuilder():
    
    def __init__(self):
        import src.multinomial_classification.run_classifier as classify
        self.classifier = classify.Classifier()
        self.extractor = TypeExtractor()
        
        # Set up the bounding and superlative handler
        self.operatorHandler = OperatorHandler()
    
    
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
                where = self.__matchWhere(table.dat[col][0][0], token)
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
                        where = self.__matchWhere(table.dat[col][0][0], tryName)
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
                where += self.__matchWhere(table.dat[matchOr[1]][0][0], matchOr[0])
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
    
    
    def __constraintSimplification(self, constr):
        '''
        The structure of the constraints is a list of lists of lists. There is an implicit AND
        between each of the outer most terms, and an implicit OR between each of the second-layer
        terms. The inner-most layer holds the component words of the constraint. For example:
        [[[price, <, 500] OR [worth, < 500]] AND [[rooms, BETWEEN, 3, 5]]]
        '''
        
        # We want to make a comparison between two different terms for each pair of terms in
        # the list. Therefore, we iterate over the list with indices i and j. The order of
        # the two terms compared does not matter, so we only make one comparison for each
        # pair (the comparison logic is symmetric).
        # For example, on the set {A, B, C}, we would make three comparisons: {A, B}; {A, C};
        # and {B, C}. Or in a graph:
        #    A B C
        #  A   B C
        #  B     C
        #  C
        # where i is the row and j is the column.
        
        breakUp = 0
        i = 0
        while i < len(constr):
            j = i + 1
            while j < len(constr):
                # We also want to iterate over every term (though typically there is only one)
                # in the OR clause. We use ii as the iterator over terms in i, and jj for j.
                ii = 0
                while ii < len(constr[i]):
                    first = constr[i][ii]
                    jj = 0
                    while jj < len(constr[j]):
                        second = constr[j][jj]
                        # no simplification if the constraints are on different attributes
                        if first[0] != second[0]:
                            jj += 1
                            continue
                        
                        # We can combine into BETWEEN if the operations are
                        #  opposite inclusive bounds that overlap (<= and >=)
                        
                        # If the attributes do match, then we need to perform case analysis on the operators
                        # < and <= can be simplified by a lower < or <= or BETWEEN
                        # > and >= can be simplified by a higher > or >= or BETWEEN
                        # BETWEEN is a combination of both a >= and a <=
                        # != cannot be simplified, unless in the case of duplication
                        fVal = float(first[2])
                        sVal = float(second[2])
                        
                        action = None
                        merge = None
                        if first[1] == '<' or first[1] == '<=':
                            if second[1] == first[1]:
                                action = fVal <= sVal
                            # Check for a combination into BETWEEN
                            elif first[1] == '<=' and second[1] == '>=' and fVal >= sVal:
                                second[1] = 'BETWEEN'
                                second.append(first[2])
                                action = False
                            elif second[1] == '>' or second[1] == '>=' and fVal <= sVal:
                                # If we find contradictory requirements, we merge them into
                                #  one OR clause.
                                merge = [first, second]
                        elif first[1] == '>' or first[1] == '>=':
                            if second[1] == first[1]:
                                action = fVal >= sVal
                            # Check (again) for a combination into BETWEEN
                            elif first[1] == '>=' and second[1] == '<=' and fVal <= sVal:
                                first[1] = 'BETWEEN'
                                first.append(second[2])
                                action = True
                            elif second[1] == '<' or second[1] == '<=' and fVal >= sVal:
                                merge = [second, first]
                        elif first[1] == '=' or first[1] == '!=' and second[1] == first[1] and fVal == sVal:
                            action = True
                        elif (first[1] == 'BETWEEN' or first[1] == 'NOT BETWEEN') and second[1] == first[1]:
                            if fVal <= sVal and first[3] >= second[3]:
                                action = True
                            elif fVal >= sVal and first[3] <= second[3]:
                                action = False
                        
                        if action is not None:
                            # reflect the temporaries back to their container
                            constr[i][ii] = first
                            constr[j][jj] = second
                            # If some action is needed, we need to determine what we are going to do.
                            # We want to delete from the option with more OR constrains.
                            # True action means the values of the first remain, false indicates of the second
                            if len(constr[i]) >= len(constr[j]):
                                if action: # if the first had the important info, copy it to the second
                                    constr[j][jj] = first
                                # Delete the first
                                constr[i].pop(ii)
                                ii -= 1
                                breakUp = 1
                                if len(constr[i]) == 0:
                                    constr.pop(i)
                                    i -= 1
                                    breakUp += 2
                            else:
                                if not action:
                                    constr[i][ii] = second
                                constr[j].pop(jj)
                                continue
                                if len(constr[j]) == 0:
                                    constr.pop(j)
                                    j -= 1
                                    breakUp = 2
                        
                        if merge is not None and len(constr[i]) == 1 and len(constr[j]) == 1:
                            # it only makes sense to merge if both are single in their or list
                            constr[j] = merge
                            constr.pop(i)
                            i -= 1
                            breakUp = 4
                        
                        if breakUp > 0:
                            breakUp -= 1
                            break
                        jj += 1
                    if breakUp > 0:
                        breakUp -= 1
                        break
                    ii += 1
                if breakUp > 0:
                    breakUp -= 1
                    break
                j += 1
            if breakUp > 0:
                break
            i += 1
        return constr
    
    
    def type3Where(self, typed:[[string, int]], table:database.Table) -> [string]:
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
                        elif typed[j][1] == 4 and self.operatorHandler.isBoundOperation(typed[j][0]):
                            if bound is not None:
                                break # cannot have two bounds!
                            bound = typed[j][0]
                            bb = self.operatorHandler.isBoundOperation(typed[j][0])
                            rest = bound[len(bb):]
                            bound = bb
                            if rest.find('(') != -1 and rest.find(')') != -1:
                                # the unit is inside the bound
                                start = rest.find('(')+1
                                end = rest.find(')')
                                unit = rest[start:end]
                            if unit is not None:
                                break # don't need to go back more if we have the bound and the unit
                        elif (bound is None or bound == '!=') and typed[j][0] == '-' and j>i: # we found a range indicator (though this can only come after and with no other bound)
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
                    # TODO: If we find multiple matches for the unit, or no unit given, we should check for type 2: "mileage less than 500"
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
                        
                        bb = '=' # equals is the assumed bounding operation.
                        if bound is not None:
                            # We assume that the bound is in a correct form (since it is defined in a file we control).
                            #  Therefore, since SQL supports >, >=, <, and <=, we can simply use it in the where clause
                            bb = bound
                        
                        where = []
                        for unitMatch in cols:
                            if otherVal is None: # no range, normal path
                                where.append([unitMatch, bb, value])
                            else:
                                bb = 'BETWEEN'
                                if bound == '!=':
                                    bb = 'NOT ' + bb
                                where.append([unitMatch, bb, value, otherVal])
                        ret.append(where)
        
        # Before we return, we want to perform basic constraint simplification.
        # Right now, the structure of ret is:
        # [[[attr operation value] ...ORedVals] ...allConstraints]
        # A complete optimization would require a case analysis for each pair of operations and some knowledge
        # about the attributes themselves (such as a knowledge of discrete/integer or continuous). Instead, we
        # will perform basic optimization only on pairs of same operation type.
        ret = self.__constraintSimplification(ret)
        # Lastly, we are going to convert the arrays into a list of strings
        clauses = []
        for orList in ret:
            where = ''
            for constraint in orList:
                if len(where) > 0:
                    where += ' OR '
                
                where += constraint[0]
                if len(constraint) > 3:
                    where += (' ' + constraint[1] + ' ' + constraint[2] + ' AND ' + constraint[3])
                else:
                    where += (' ' + constraint[1] + ' ' + constraint[2])
            if len(where) > 0:
                clauses.append(where)
        return clauses
    
    
    def orderBy(self, typed:[[string, int]], table:database.Table, type3:[string]) -> [string]:
        # Since we assume the query has already been standardized, we can go through quickly looking for superlative tokens
        ret = []
        usedAttrs = []
        
        for token in typed:
            superlative = self.operatorHandler.isSuperlative(token[0])
            if superlative:
                # We have identified a superlative. By definition, we have an affected list
                rest = token[0][len(superlative):]
                start = rest.find('(')+1
                end = rest.find(')')
                affected = rest[start:end].split(', ')
                
                # Now we need to find out how the affected applies in the context of our table
                attrFound = None
                for affect in affected:
                    if affect[0] == '_': # This is indicative of a attribute value
                        attrVal = affect[1:].lower()
                        # We will search the table attribute names (and synonyms) to try to find a match
                        for attr in table.dat:
                            for name in attr[0]:
                                if attrVal == name:
                                    attrFound = attr[0][0]
                                    break
                            if attrFound is not None:
                                break
                        if attrFound is not None:
                                break
                    else: # otherwise, we treat the affected like a unit
                        unitVal = affect.lower()
                        # We will search the table unit names to find a match
                        for attr in table.dat:
                            if len(attr) > 2:
                                for unit in attr[2]:
                                    if unitVal == unit:
                                        attrFound = attr[0][0]
                                        break
                                if attrFound is not None:
                                    break
                        if attrFound is not None:
                                break
                
                # Lastly, we just need to find if it is ascending (<<) or descending (>>)
                if superlative == "<<":
                    ret.append(attrFound + " ASC")
                elif superlative == ">>":
                    ret.append(attrFound + " DESC")
                else:
                    attrFound = None
                
                if attrFound is not None:
                    usedAttrs.append(attrFound)
        
        # We can also take advantage of the logic used to calculate type III constraints. If the user says "less than $3,000", then we can
        #  assume they are looking to minimize cost. This is an example of a secondary superlative (cheapest in this case).
        #  It may not be as important as the explicit superlatives, but if the condition is not met, we should order partials.
        
        # We don't want to worry about more complex clauses that contain OR since our ordering assumption is not necessarily valid
        for i in range(len(type3)):
            constr = type3[i]
            if 'OR' in constr:
                continue
            # the attribute is always the first in the constraint (even for between)
            comps = constr.split(' ')
            if comps[0] in usedAttrs:
                continue # do not reuse any attribute
            
            usedAttrs.append(comps[0]) # add it to used since we are analyzing it now
            # Look through all the other constraints to verify there aren't conflicting reqs
            ok = True
            for j in range(i+1, len(type3)):
                other = type3[j]
                if comps[0] in other and not(len(other) > 0 and other[0] == '('):
                    # The other has valid form. We want to verify it does not conflict with this
                    if comps[1] == '<' or comps[1] == '<=' and '<' in other:
                        ok = True
                    elif comps[1] == '>' or comps[1] == '>=' and '>' in other:
                        ok = True
                    else: # otherwise, they are conflicting
                        ok = False
                        break
            
            # If no conflicting was found, we can use this for ordering partials
            if ok:
                if '>' in comps[1]:
                    ret.append(comps[0] + " DESC")
                elif '<' in comps[1]:
                    ret.append(comps[0] + " ASC")
                elif '=' in comps[1] or 'BETWEEN' in comps[1]:
                    if 'BETWEEN' in comps[1]:
                        mean = (float(comps[2]) + float(comps[4])) / 2
                    else:
                        mean = comps[2]
                    ret.append(f'ABS({mean} - {comps[0]})')
        
        return ret
    
    
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
    
    
    def correctSpelling(self, tokens, domain, table):
        # To do so, we need to have a big dictionary with all three types of the correct domain
        trieList = self.extractor.verifier.getDomainTries(domain)
        allWords = []
        for trie in trieList:
            for word in trie.wordSet:
                allWords.append(word.lower())
        # There are also some words that are universal (not specific to domain)
        #  examples are the boundary words and the superlative words
        for bounder in self.operatorHandler.bounders:
            for phrase in bounder[1]:
                for word in phrase.split(' '):
                    # There are some tokens that we should not add as words, namely the
                    #  wild card (*) and applications (parenthesized application codes)
                    if not('(' in word or ')' in word or word=='*'):
                        allWords.append(word)
        for superlative in self.operatorHandler.superlatives:
            for phrase in superlative[1]:
                for word in phrase.split(' '):
                    # There are some tokens that we should not add as words, namely the
                    #  wild card (*) and applications (parenthesized application codes)
                    if not('(' in word or ')' in word or word=='*'):
                        allWords.append(word)
        for key in self.operatorHandler.boundApps.keys():
            for synonym in self.operatorHandler.boundApps[key]:
                allWords.append(synonym)
        universal = ['and', 'or', 'not', 'between', 'from']
        allWords += universal
        
        # There are also domain-specific words we will enter
        for attr in table.dat:
            for typeSynonym in attr[0]:
                allWords.append(typeSynonym)
            if len(attr) > 2:
                for unit in attr[2]:
                    allWords.append(unit)
        # Now we can actually perform the spelling corrections (if any)
        from src.trie.symspell import spell_corrector
        words_dict = {}
        for word in allWords:
            if word in words_dict:
                words_dict[word] += 1
            else:
                words_dict[word] = 1
                
        return spell_corrector(tokens, words_dict)
    
    
    def extractOperated(self, typed, table, domain):
        result = OperatorEvaluator(typed[:], lambda x: self.operatorHandler.isBoundOperation(x) or self.operatorHandler.isSuperlative(x)).result
        
        # Now we need to read through the structure and work on the subparts
        # Essentially, we are trying to flatten it. 
        def flatten(resList):
            # For non-relation items, we can add them to a list that we can analyze through our type methods.
            typesWhere = [[], [], []]
            # However, relation items are more complicated, since they can analyze other relations and/or others.
            def contribute(relation) -> [[string]]:
                typesWhere = [[], [], []]
                if isinstance(relation, NotRelation):
                    # We want to get the result of flattening the internals
                    notted = flatten(relation.notted)
                    # We can append each clause with NOT (since that is valid in SQL)
                    j = 0
                    while j < len(notted):
                        typeNum = notted[j]
                        for clause in typeNum:
                            typesWhere[j].append('NOT ' + clause)
                        j += 1
                elif isinstance(relation, AndRelation):
                    left = flatten(relation.left)
                    right = flatten(relation.right)
                    # For and, we just want to add all clauses from both sides
                    all_ = [left, right]
                    for side in all_:
                        j = 0
                        while j < len(side):
                            typeNum = side[j]
                            typesWhere += typeNum
                elif isinstance(relation, OrRelation):
                    left = flatten(relation.left)
                    right = flatten(relation.right)
                    # Or is likely the hardest, since we need to combine all subclauses into one giant anded list (for each side)
                    # then we combine those sides into a large OR statement
                    lefted = ''
                    righted = ''
                    # Unfortunately, we have to sacrifice the type distinction. Though this is ok, since we only needed it for optimization,
                    #  which would not be possible in the large or statement anyway
                    for typeNum in left:
                        for clause in typeNum:
                            if len(lefted) > 0:
                                lefted += ' AND '
                            lefted += clause
                    for typeNum in right:
                        for clause in typeNum:
                            if len(righted) > 0:
                                righted += ' AND '
                            righted += clause
                    ored = ''
                    if len(lefted) > 0:
                        ored = lefted
                    if len(righted) > 0:
                        missEnd = False
                        if len(ored) > 0:
                            ored = '(' + ored + ') OR ('
                            missEnd = True
                        ored += righted
                        if missEnd:
                            ored += ')'
                    if len(ored) > 0:
                        typesWhere[0].append(ored)
                return typesWhere
            
            pending = []
            def clearPending():
                # process the tokens and add them to their respective lists, then clear the pending list
                if len(pending) > 0:
                    typesWhere[0] += self.type1Where(pending, table)
                    typesWhere[1] += self.type2Where(pending, table, domain)
                    typesWhere[2] += self.type3Where(pending, table)
                    pending.clear()
            
            i = 0
            while i < len(resList):
                if isinstance(resList[i], OperatorRelation):
                    # If we encountered a non-operator item, then it splits the pending list
                    clearPending()
                    
                    # Now we want to handle all that the relation contained
                    contributed = contribute(resList[i])
                    typesWhere[0] += contributed[0]
                    typesWhere[1] += contributed[1]
                    typesWhere[2] += contributed[2]
                else:
                    pending.append(resList[i])
                i += 1
            # If we have left the loop, we want to make one final check for pending
            clearPending()
            return typesWhere
        
        # Return the results of starting the recursive method
        return flatten(result)
    
    
    def fromQuery(self, query:string, log):
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
        table = getTable(domain)
        log("Identified as:", domain.name.lower())
        
        # We want to tokenize the query
        tokens = self.tokenize(query.lower())
        
        # and then correct any misspellings
        log("Correcting spelling...")
        tokens = self.correctSpelling(tokens, domain, table)
        log('"' + " ".join(tokens) + '"')
        
        # now we want to pull some data out (Type I, II, III)
        typed = self.extractor.typify(tokens, domain)
        # And standardize what we find
        standardizer = Standardizer(self.operatorHandler)
        typed = standardizer.standardizeQuery(typed)
        log("Typed query:")
        log(typed, '\n')
        
        # Now we want to start building the query.
        #  It is going to be in the form of a SELECT statement, with an AND for each of the types that need to be matched
        #  For example, SELECT * FROM table WHERE typeI AND typeII AND typeIII
        
        # We will only want one set of constraints at the end, but explicit boolean operators will have us split the query
        # into separate pieces that should be evaluated in a specific relation to each other.
        typeReqs = self.extractOperated(typed, table, domain)
        
        # Print out what we got for debugging purposes
        typeIWhere = typeReqs[0]
        log('I:', typeIWhere)
        typeIIWhere = typeReqs[1]
        log('II:', typeIIWhere)
        typeIIIWhere = typeReqs[2]
        log('III:', typeIIIWhere)
        
        orderByClause = self.orderBy(typed, table, typeIIIWhere)
        log('order:', orderByClause)
        # We can use the LIMIT clause to limit the number of responses. Generally, we don't want more than 10 at a time
        return [table, typeIWhere, typeIIWhere, typeIIIWhere, orderByClause]


if __name__ == '__main__':
    '''Here are some sample queries to use:
    Fabricated examples:
    '200,000 miles or less cheapest blue Kawasaki Ninja 400'
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
    'honda odyssey mileage less than 30,000 miles and less than 50,000 miles.'
    '200,000 miles or less and 300,000 miles or less, price between $50-60, blue Kawasaki Ninja'
    'not between 10,000 miles and 200,000 miles, price between $500-600, blue Kawasaki Ninja'
    'not not not less than 50,000 miles Honda Odyssey'
    'not surpassing 50,000 miles Honda Odyssey not most expensive'
    'kitchen countertop granite or < $200, black or brown'
    
    Mechanical Turk queries:
    'red or green cedar and cherry nightstands for $1000 or less and at least 2" high'
    'jewelry weeding collections $50000'
    'TOYOTA MOTORCYCLE SECOND HAND $10000 BLUE COLOR  300,000 MILAGE'
    'anniversary chain for her silver or gold $300'
    
    Tricky reduction queries:
    'honda accord red like new haven' -> [honda] [accord] [red] (([like new] [haven]) \/ [new haven])
    'honda accord red new haven' -> [honda] [accord] [red] (([new] [haven]) \/ [new haven])
    'honda accord red like new' -> [honda] [accord] [red] ([like new] \/ [new])
    'honda accord red new' -> [honda] [accord] [red] ([new] \/ [new])
    '''
    
    cb = ConstraintBuilder()
    import sys
    print('"' + sys.argv[1] + '"')
    
    toLog = True
    if toLog:
        def log(*args):
            for a in args:
                print(a, end=' ')
            print()
    else:
        def log(*args):
            pass
    
    reqs = cb.fromQuery(sys.argv[1], log)
    log() # get a new line
    
    # Here we will employ the partial matcher to refine our results.
    #  We will modify some of the constraints
    sql = PartialMatcher().bestRequest(reqs, log)
    print(sql, '\n')
    
    from src.database import execute
    res = execute(sql)
    print(len(res), 'Results:')
    for result in res:
        print('', result)
    
