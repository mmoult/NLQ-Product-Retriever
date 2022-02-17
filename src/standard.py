
class Standardizer(object):

    def __init__(self, operatorHandler):
        self.operatorHandler = operatorHandler
    
    
    import string
    def standardizeQuery(self, typed:[[string, int]]) -> [[string, int]]:
        # Go through each of the bounders and try to match them to tokens in the query
        for bounder in self.operatorHandler.bounders:
            sym = bounder[0]
            for option in bounder[1]:
                # For each option that maps to the given symbol
                #  We will want to break each option into component tokens
                comps = option.split(' ')
                changes = True # we will cycle through the typified query tokens until no changes can be made
                while changes:
                    changes = False
                    unit = '' # the units found
                    useIndicator = '' # if this must come at the end (.), or can be end or beginning (,)
                    i = 0 # the current component index to match with
                    start = 0
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
                            elif comps[i] == token[0].lower(): # we need an exact match
                                i += 1 # go to the next component to match
                                
                                # Check for an application next or use indicator (',' or '.')
                                if i < len(comps):
                                    if comps[i][0] == '(' and comps[i][-1] == ')':
                                        # we found an application. This should be saved, but then skipped over
                                        if len(unit) > 0:
                                            unit += ' '
                                        
                                        appCode = comps[i][1:-1]
                                        if appCode in self.operatorHandler.boundApps:
                                            # match of application definition
                                            if len(unit) > 0:
                                                unit += ' '
                                            unit += ' '.join(self.operatorHandler.boundApps[appCode])
                                        i += 1 # move on, since we don't actually match against an application
                                    elif len(comps[i]) == 1 and (comps[i] == ',' or comps[i] == '.'):
                                        useIndicator = comps[i]
                                        i += 1 # move on, since we don't match on the use indicator
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
                        if len(useIndicator) > 0:
                            value += ' [' + useIndicator + ']'
                        typed = typed[0:start] + [[value, 3]] + typed[end+1:]
                        changes = True
        
        # Check to see if the tokens match with superlatives. This algorithm closely resembles for bounding.
        #  A superlative will match one of the synonyms and will either be followed by (or preceded by) a Type II attribute or a Type III unit
        for superlative in self.operatorHandler.superlatives:
            sym = superlative[0]
            for option in superlative[1]:
                # For each option that maps to the given symbol, we look in the query for potential matches
                #  each match option can contain multiple tokens, which we need to break into component parts
                comps = option.split(' ')
                changes = True # we will cycle through the typified query tokens until no changes can be made
                while changes:
                    changes = False
                    affected = '' # the unit or attribute that is being affected
                    i = 0 # the current component index to match with
                    start = 0
                    end = -1
                    for j in range(len(typed)):
                        token = typed[j]
                        reset = False
                        # We only consider the token to match the superlative if it is type 4.
                        if token[1] == 4:
                            if comps[i] == token[0].lower(): # we need an exact match
                                i += 1 # go to the next component to match
                                
                                # Check for an application
                                if i < len(comps) and comps[i][0] == '(' and comps[i][-1] == ')':
                                    # we found an application. This should be saved, but then skipped over
                                    appCode = comps[i][1:-1]
                                    if appCode in self.operatorHandler.superApps:
                                        # match of application definition
                                        affected = ', '.join(self.operatorHandler.superApps[appCode])
                                    i += 1 # move on, since we don't actually match against an application
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
                        if len(affected) == 0:
                            # If no affected was built-in to the superlative, we need to go find it
                            #  If it exists, it will either be immediately after or before the superlative
                            if end+1 <= len(typed):
                                if typed[end+1][1] == 2:
                                    # Mark Type II affected with a leading underscore
                                    affected = "_" + typed[end+1][0]
                                    end += 1
                                elif typed[end+1][1] == 3:
                                    affected = typed[end+1][0]
                                    end += 1
                            if len(affected) == 0 and start > 0 and typed[start-1][1] == 2:
                                affected = "_" + typed[start-1][0]
                                start -= 1
                        
                        # Now append the affected
                        if len(affected) > 0:
                            value += " (" + affected + ")"
                        else:
                            # If we could not find an effected, then throw out this superlative!
                            break
                        # Lastly, reflect the changes in the query
                        typed = typed[0:start] + [[value, 4]] + typed[end+1:]
                        changes = True
        
        # There are just a few different phrases for ranges:
        #  Between * (and/to/-) *
        #  From * (to/-) *
        #  * - *
        # Since the - is the common denominator in all, we will simplify to that.
        #  There should be no other cases of - by itself, since negation is without a space.
        rangeType = None
        delIndex = None
        i = 0
        while i < len(typed):
            token = typed[i]
            if token[0].lower() == 'between' or token[0].lower() == 'from':
                rangeType = token[0].lower()
                delIndex = i
            
            elif rangeType is not None:
                if token[0].lower() == 'to' or (rangeType == 'between' and token[0].lower() == 'and'):
                    token[0] = '-' # transform to a simple hyphen, maintaining type
                    typed.pop(delIndex) # we delete the starting range word (since it can interfere with finding "not")
                    i -= 1
                
                # Between the range start and the range middle, we only expect to encounter number values and units.
                elif token[1] == 3:
                    i += 1
                    continue
                # If we get anything else, break the range construct
                rangeType = None
                delIndex = None
            i += 1
        
        # Simplify any negated conditions
        i = 0
        while i < len(typed):
            if typed[i][0] == '!=':
                # We encountered a not.
                # The not must come before the condition operation that it is modifying
                if i+1 < len(typed):
                    nxt = typed[i+1][0]
                    if nxt == '!=':
                        # Two nots cancel out
                        typed.pop(i)
                        typed.pop(i)
                        continue
                    
                    isBound = self.operatorHandler.isBoundOperation(nxt)
                    isSuper = self.operatorHandler.isSuperlative(nxt)
                    isOp = isBound if isBound is not None else isSuper
                    if isOp is not None:
                        excess = nxt.rfind('(')
                        if excess != -1:
                            excess = nxt[excess:]
                        else:
                            excess = ""
                        
                        result = None
                        if isOp == '<':
                            result = '>='
                        elif isOp == '<=':
                            result = '>'
                        elif isOp == '>':
                            result = '<='
                        elif isOp == '>=':
                            result = '<'
                        elif isOp == '<<':
                            result = '>>'
                        elif isOp == '>>':
                            result = '<<'
                        
                        if result is not None:
                            if len(excess) > 0:
                                result += ' ' + excess # append the qualifiers
                            typed[i][0] = result
                            typed.pop(i+1)
            i += 1
        return typed
        