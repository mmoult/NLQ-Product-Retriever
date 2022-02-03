
class SimilarityGraph():
    def __init__(self):
        self.nodes = dict()
    
    def nodeOf(self, name):
        if name in self.nodes:
            return self.nodes[name]
        # If the node was not found, we want to create and put it in.
        node = GraphNode(name)
        self.nodes[name] = node
        return node
    
    def bidirection(self, head, tail, cost = 1):
        n1 = self.nodeOf(head)
        n2 = self.nodeOf(tail)
        
        n1.connect(n2, cost)
        n2.connect(n1, cost)
    
    def direction(self, head, tail, cost = 1):
        n1 = self.nodeOf(head)
        n2 = self.nodeOf(tail)
        
        n1.connect(n2, cost)
    
def createFromStringLines(text):
    graph = SimilarityGraph()
    for line in text:
        line = line.lower()
        # We want to find the divider between the two nodes (if this line is not blank)
        if len(line) == 0:
            continue
        
        def splitComps(line, conn):
            # Edges are specified as: <N1> <connection> <N2> $ <cost>
            left = line[:split].strip()
            right = line[split + len(conn):].strip()
            costFound = right.find('$')
            if costFound != -1:
                cost = right[costFound + 1:].strip()
                right = right[:costFound].strip()
                return (left, right, float(cost))
            return (left, right, 1)
        
        # The dividers are '<->' for bidirectional, '->' or '<-' for directional.
        split = line.find('<->')
        if split != -1:
            left, right, cost = splitComps(line, '<->')
            graph.bidirection(left, right, cost)
            continue
        split = line.find('<-')
        if split != -1:
            left, right, cost = splitComps(line, '<-')
            graph.direction(right, left, cost)
            continue
        split = line.find('->')
        if split != -1:
            left, right, cost = splitComps(line, '->')
            graph.direction(left, right, cost)
            continue
        raise Exception("Unexpected line '", line, '" found! Each line must list two nodes and give their relation as "<->", "<-", or "->"!')
    return graph


class GraphNode():
    def __init__(self, name):
        self.name = name
        self.connections = set()
    
    def connect(self, otherNode, cost=1):
        self.connections.add(GraphEdge(otherNode, cost))


class GraphEdge():
    def __init__(self, toNode, cost=1):
        self.toNode = toNode
        self.cost = cost


def readFileLines(path):
    from pathlib import Path
    lines = []
    with open(str(Path(__file__).parent) + path, encoding='utf-8') as file:
        while True:
            line = file.readline()
            if not line:
                break
            if line[-1] == '\n':
                line = line[:len(line) - 1]
            lines.append(line)
    return lines


class Similarity(object):
    def __init__(self, tableName):
        self.tableName = tableName
        hasFile = dict()
        
        # Unfortunately, we need to map from the table columns used in constraints to the
        #  associated files, which cannot be an elegant solution.
        from src.domains import Domain
        if tableName == Domain.CAR:
            hasFile['condition'] = 'condition'
            hasFile['type'] = 'car-type'
            hasFile['paint_color'] = 'color'
            hasFile['state'] = 'us-states'
        elif tableName == Domain.FURNITURE: # No options for furniture :/
            raise Exception("No similarity options for furniture!")
        elif tableName == Domain.HOUSING: # I could maybe match on suburb location?
            raise Exception("No similarity options for housing!")
        elif tableName == Domain.JEWELRY:
            hasFile['tags'] = 'material'
        elif tableName == Domain.JOB:
            hasFile['sector'] = 'work-sector'
            hasFile['location'] = 'us-states'
        elif tableName == Domain.MOTORCYCLE: # No options for motorcycles either :/
            raise Exception("No similarity options for motorcycles!")
        
        self.hasFile = hasFile
        # Building each graph takes a lot of work, which we don't want to do unless we need it
        self.graphs = dict()
    
    
    def valueNode(self, attr, value) -> GraphNode:
        filePrefix = "/../similarity/"
        # Get the proper graph for this attribute
        if attr in self.hasFile:
            # Excellent! We found an attribute we can partial match on
            # We must build the graph if it has not been built already
            if not attr in self.graphs:
                graph = createFromStringLines(readFileLines(filePrefix + self.hasFile[attr] + '.txt'))
                self.graphs[attr] = graph # place it in the dictionary for next time
            else:
                graph = self.graphs[attr]
            
            # try to find the node in attr's graph that matches the specified value
            if value in graph.nodes:
                return graph.nodes[value]
        # Return nothing if we could not find specified
        return None


def suggestReplacements(tableName, constraints):
    replacements = [None for _ in range(len(constraints))]
    
    try:
        similarity = Similarity(tableName)
    except:
        # If there was an exception, then there are no matches for that table name
        return replacements
    
    # Now we are going to go through each constraint and suggest potential alternatives
    for i in range(len(constraints)):
        changed = False
        constr = constraints[i]
        
        # We will look on operations that we can partial match on
        operations = [' LIKE "% ', ' = ', ' < ', ' <= ', ' > ', ' >= ']
        indx = 0 # for some reason it needs to start within range
        partialOp = "default"
        
        # No such thing as a do-while loop in Python, so we must use this strange construct
        while partialOp is not None:
            if partialOp != "default":
                # We can find the attribute operated on, which is common logic to all operations
                breakIndex = indx - 1
                while breakIndex > -1:
                    # go backwards until we either find a break or the beginning of the string
                    if constr[breakIndex] == ' ' or constr[breakIndex] == '(':
                        break
                    breakIndex -= 1
                attr = constr[breakIndex + 1:indx]
                
                newClause = None
                if partialOp == ' LIKE "% ':
                    # try to find the node with value matching given value from the constraint
                    end = constr.index(' %"', indx + 9)
                    matchValue = constr[indx + 9:end]
                    end += 3
                    node = similarity.valueNode(attr, matchValue)
                    if node is not None:
                        # Excellent! We found an attribute we can partial match on
                        neighbors = node.connections
                        # Lastly, we build a giant OR with all the neighboring values 
                        #  (We don't exclude matchValue since it may be helpful to match
                        #  on with our liberal replacement strategy.)
                        newClause = '(' + attr + ' LIKE "% ' + matchValue + ' %"'
                        for edge in neighbors:
                            if edge.cost <= 1:
                                newClause += ' OR ' + attr + ' LIKE "% ' + edge.toNode.name + ' %"'
                        newClause += ')'
                    if newClause is None:
                        indx += 13 # 13 is length of pattern ' LIKE "% x %"'
                   
                else: # We can also suggest replacements for numeric type III values
                    # all operations here need a matchValue float to use
                    end = indx + len(partialOp)
                    while end < len(constr):
                        # go forwards until some break
                        if constr[end] == ' ' or constr[end] == ')':
                            break
                        end += 1
                    matchValue = float(constr[indx + len(partialOp):end])
                    import math
                    offs = math.ceil(math.log(matchValue) / 2)
                    loBound = str(matchValue - offs)
                    hiBound = str(matchValue + offs)
                    if partialOp == ' = ':
                        newClause = '(' + attr + ' BETWEEN ' + loBound + ' AND ' + hiBound + ')'
                    elif partialOp == ' < ' or partialOp == ' <= ':
                        newClause = attr + partialOp + hiBound
                    elif partialOp == ' > ' or partialOp == ' >= ':
                        newClause = attr + partialOp + loBound
                
                if newClause is not None:
                    changed = True
                    # Now we need to insert our new clause to replace what was there
                    constr = constr[:breakIndex + 1] + newClause + constr[end:]
                    # Finally we want to calculate how many to skip ahead in the search
                    indx = breakIndex + len(newClause)    
            
            # find a new operation
            partialOp = None
            lowest = len(constr)
            for pop in operations:
                got = constr.find(pop, indx)
                if got != -1 and got < lowest:
                    lowest = got
                    partialOp = pop
            indx = lowest
            # Then we restart the loop. If we found some operation to match on, then do it and check again
        
        if changed: # leave the "replacement" as None if there were no partial-match changes
            replacements[i] = constr
    return replacements
