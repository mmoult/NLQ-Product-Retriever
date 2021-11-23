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


    def generateRemovals(self, remove, listSize, ordered):
        """
        Generates and returns all possible removal combinations for a specific list size.
        @param remove: the number of entries to remove in the solutions. This value should
                       not exceed the list size (since empty list cannot be removed from)
        @param listSize: the size of the list removing from
        @param ordered: whether the order of the removals is important. For example, if
                        removing 2 from a 3-entry list, there will be three solutions if
                        order does not matter (one for each remaining value), but if
                        order does matter, there will be six solutions.
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
        rec = self.generateRemovals(remove - 1, listSize - 1, ordered)
        for i in range(listSize):
            for recEntry in rec:
                removals.append([i] + recEntry)
        return removals
    
    
    def bestRequest(self, requirements, log) -> string:
        # [table, typeIWhere, typeIIWhere, typeIIIWhere, orderByClause]
        table = requirements[0]
        type1 = requirements[1]
        type2 = requirements[2]
        type3 = requirements[3]
        constr = type1 + type2 + type3
        order = requirements[4]
        
        query = self.fromConstraints(table.name, constr, order)
        
        # The hope is that the query runs just fine and gives us some results.
        res = execute(query)
        
        # However, this is not guaranteed to be the case. Sometimes the user may not get any results,
        #  in which case, we want to modify the query for them to get something similar
        scheduler = []
        round = 0
        while len(res) == 0:
            # Make each constraint optional (one by one) until we get something
            constraints = constr
            if len(scheduler) == 0:
                # if the scheduler is empty, then we need to move to the next round and refill it
                round += 1
                scheduler = self.generateRemovals(round, len(constraints))
            
            break
        
        
        return query
