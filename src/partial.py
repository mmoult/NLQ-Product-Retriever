import string
from src.database import execute


class PartialMatcher(object):
    '''
    The class will take some query requirements and pare them down if necessary
    in order to get results.
    '''
    
    def fromConstraints(self, tableName, constr, orderBy) -> string:
        query = 'SELECT * FROM ' + tableName
        if len(constr) > 0:
            query += ' WHERE '
            first = True
            for constraint in constr:
                if first:
                    first = False
                else:
                    query += ' AND '
                query += ('(' + constraint + ')')
        if len(orderBy) > 0:
            ' ORDER BY '
            first = True
            for order in orderBy:
                if first:
                    first = False
                else:
                    query += ', '
                query += order
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
    
    
    def bestRequest(self, requirements, log) -> string:
        # [table, typeIWhere, typeIIWhere, typeIIIWhere, orderByClause]
        table = requirements[0]
        type1 = requirements[1]
        type2 = requirements[2]
        type3 = requirements[3]
        constr = type1 + type2 + type3
        order = requirements[4]
        
        log(len(constr), 'total constraints...')
        query = self.fromConstraints(table.name, constr, order)
        
        # The hope is that the query runs just fine and gives us some results.
        res = execute(query)
        
        # However, this is not guaranteed to be the case. Sometimes the user may not get any results,
        #  in which case, we want to modify the query for them to get something similar
        scheduler = [[]]
        rnd = 0
        roundConstr = []
        while len(res) == 0:
            # Make each constraint optional (one by one) until we get something
            constraints = constr
            if len(scheduler) == 0:
                # if the scheduler is empty, then we need to move to the next round and refill it
                # Though, if we got successful queries last round, we can just break
                if len(roundConstr) > 0:
                    break
                rnd += 1
                if rnd >= len(constraints):
                    break # we cannot remove all or more constraints than we have
                log('Round 1')
                scheduler = self.generateUnorderedRemovals(rnd, len(constraints))
            
            # Go forward with the schedule
            rems = scheduler.pop(0)
            for rem in rems:
                constraints.pop(rem)
            query = self.fromConstraints(table.name, constraints, order)
            res = execute(query)
            if len(res) > 0: # We got a successful query!
                # Add the constraints to the list and keep looking for the rest of the round
                roundConstr.append(constraints)
        
        if len(roundConstr) > 0:
            constraints = ''
            # OR together all successful constraints
            firstRound = True
            for roundC in roundConstr:
                if firstRound:
                    firstRound = False
                else:
                    constraints += ' OR '
                
                constraints += '('
                first = True
                for constraint in roundC:
                    if first:
                        first = False
                    else:
                        constraints += ' AND '
                    constraints += ('(' + constraint + ')')
                constraints += ')'
        else:
            constraints = constr
        
        return self.fromConstraints(table.name, constraints, order)
