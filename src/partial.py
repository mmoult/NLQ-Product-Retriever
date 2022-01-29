import string
from src.database import execute
from src.content_match import suggestReplacements


class PartialMatcher(object):
    '''
    The class will take some query requirements and pare them down if necessary
    in order to get results.
    '''
    
    def __buildWhere(self, constr):
        where = ''
        first = True
        for constraint in constr:
            if first:
                first = False
            else:
                where += ' AND '
            where += ('(' + constraint + ')')
        return where
    
    
    def __buildOrder(self, constr):
        orderBy = ''
        first = True
        for order in constr:
            if first:
                first = False
            else:
                orderBy += ', '
            orderBy += order
        return orderBy
    
    
    def fromConstraints(self, tableName, constr, orderBy, limit) -> string:
        query = 'SELECT * FROM ' + tableName.value
        if len(constr) > 0:
            query += ' WHERE '
            query += self.__buildWhere(constr)
        if len(orderBy) > 0:
            query += ' ORDER BY '
            query += self.__buildOrder(orderBy)
        if limit >= 0:
            query += " LIMIT " + str(limit)
        return query


    def generateUnorderedRemovals(self, remove, listSize, start=0):
        """
        Generates and returns all possible unordered removal combinations for a specific list
        size and number of removals.
        @param remove: the number of entries to remove in the solutions. This value should
                       not exceed the list size (since empty list cannot be removed from)
        @param listSize: the size of the list removing from
        @return the removal solutions. It is assumed that when an entry is removed, the
                entire list is shifted down. Therefore, [0, 0, 0] is possible for 3
                removals since it will remove the beginning of the list three times.
                The type is [[int]], a list of solutions, where each solution is a list
                of the indices needing to be removed (in the removal order).
        """
        
        if remove < 1:
            return [[]]
        if listSize == 1:
            return [[0]]
        elif listSize == 0:
            raise Exception("Cannot remove from an empty list!")
        
        removals = []
        for i in range(start, listSize - remove + 1):
            rec = self.generateUnorderedRemovals(remove - 1, listSize - 1, i)
            for j in rec:
                removals.append([i] + j)
        return removals
    
    
    def bestResults(self, requirements, log, limit):
        # [table, typeIWhere, typeIIWhere, typeIIIWhere, orderByClause]
        table = requirements[0]
        type1 = requirements[1]
        type2 = requirements[2]
        type3 = requirements[3]
        constr = type1 + type2 + type3
        order = requirements[4]
        
        log(len(constr), 'total constraints...')
        
        # However, this is not guaranteed to be the case. Sometimes the user may not get any results,
        #  in which case, we want to modify the query for them to get something similar
        
        # We can perform partial content matching on Type I and Type II results
        # We will create a list of partial-match replacements to parallel constr
        replacements = suggestReplacements(table.name, constr)
        
        # We want to keep searching for results until the limit is reached
        results = []
        rnd = 0
        doPartial = True
        scheduler = [[]]
        while len(results) < limit or limit == -1:
            roundConstr = []
            contentSuccess = False
            while True:
                # Make each constraint optional (one by one) until we get something
                if len(scheduler) == 0:
                    # if the scheduler is empty, then we need to move to the next round and refill it
                    # Though, if we got successful queries last round, we can just break
                    if len(roundConstr) > 0:
                        break
                    rnd += 1
                    # Since we are going to the next round, we want to try partials again.
                    doPartial = True
                    if rnd >= len(constr):
                        break # we cannot remove all or more constraints than we have
                    log('Round', rnd)
                    scheduler = self.generateUnorderedRemovals(rnd, len(constr))
                
                # Go forward with the schedule
                rems = scheduler.pop(0)
                
                # Try a content-based partial match, and if no success, try without
                def tryQuery(constraints):
                    query = self.fromConstraints(table.name, constraints, order, limit)
                    res = execute(query)
                    if len(res) > 0:
                        log('success:', query)
                    else:
                        log('try:', query)
                    return len(res) > 0
                
                constraints = constr[:] # make a clone of the constraint list that we will manipulate
                indices = list(range(len(constraints)))
                remCpy = rems[:]
                # Since indices is just a list of ordered, counting integers, we can use the ones popped
                #  as indices to replace in constraints from the partial match
                changed = False
                # We don't do partial if we backtrack (to reach limit) a round and already had success with it.
                if doPartial:
                    for rem in remCpy:
                        index = indices.pop(rem)
                        if replacements[index] is not None:
                            constraints[index] = replacements[index]
                            changed = True
                    if changed: # only do a content-based partial match if the constraints were changed!
                        if tryQuery(constraints):
                            # The partial match was successful!
                            # This is big news, since a content-based partial is preferred over a removal.
                            if not contentSuccess:
                                contentSuccess = True
                                roundConstr.clear()
                            roundConstr.append(constraints)
                            continue # skip the removal of the indices, since partial was sufficient
                        constraints = constr[:]
                
                # Now try removing the specified indices
                if contentSuccess:
                    # don't bother trying removals if we had success with content partial this round.
                    continue # But we have to finish the round in case there are other partials to be found.
                for rem in rems:
                    constraints.pop(rem)
                if tryQuery(constraints):
                    roundConstr.append(constraints)
                # Interestingly, we continue to the next schedule in the round, even if we find a success.
                #  Even though we achieved success with this removal, we have no certainty that this removal
                #  was any more valid than any other removal. We need to test all the different possibilities
                #  in the round before we can make a decision. 
                # If a round is successful, we do not need to continue to the next round (Each round removes
                #  more from the constraint list, and logically builds upon the previous round).
        
            if len(roundConstr) > 0:
                constraints = ''
                # OR together all successful constraints
                firstRound = True
                for roundC in roundConstr:
                    if len(roundC) == 0:
                        continue
                    
                    if firstRound:
                        firstRound = False
                    else:
                        constraints += ' OR '
                    
                    constraints += ('(' + self.__buildWhere(roundC) + ')')
            else:   # If we exited without adding round constraints, we eliminated all constraints with no success
                    # Therefore, we should rely on ordering
                constraints = ''
        
            query = 'SELECT * FROM ' + table.name.value
            if len(constraints) > 0:
                query += (' WHERE ' + constraints)
            if len(order) > 0:
                query += ' ORDER BY '
                query += self.__buildOrder(order)
            if limit >= 0:
                query += " LIMIT " + str(limit)
        
            # Add from the query to the results
            res = execute(query)
            # Filter out any duplicates
            for result in res:
                if result not in results:
                    # Should always add to the end of the result list
                    results.append(result)
            
            print("Found", len(results), '/', limit)
            log()
            
            if constraints == '':
                break # Cannot check more constraints if there are simply no matches...
            
            # If content success was true, then we should go back to that round without partials
            if contentSuccess:
                # Redo the last round, but without partials
                doPartial = False
                if len(results) < limit or limit == -1:
                    log("return to Round", rnd)
                    scheduler = self.generateUnorderedRemovals(rnd, len(constr))

        return results
        