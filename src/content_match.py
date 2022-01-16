
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
    
    def bidirection(self, head, tail):
        n1 = self.nodeOf(head)
        n2 = self.nodeOf(tail)
        
        n1.connect(n2)
        n2.connect(n1)
    
    def direction(self, head, tail):
        n1 = self.nodeOf(head)
        n2 = self.nodeOf(tail)
        
        n1.connect(n2)
        n2.connect(n1)
    
def createFromStringLines(text):
    graph = SimilarityGraph()
    for line in text:
        line = line.lower()
        # We want to find the divider between the two nodes (if this line is not blank)
        if len(line) == 0:
            continue
        
        # The dividers are '<->' for bidirectional, '->' or '<-' for directional.
        split = line.find('<->')
        if split != -1:
            left = line[:split]
            right = line[split + 3:]
            graph.bidirection(left, right)
            continue
        split = line.find('<-')
        if split != -1:
            left = line[:split]
            right = line[split + 2:]
            graph.direction(right, left)
            continue
        split = line.find('->')
        if split != -1:
            left = line[:split]
            right = line[split + 2:]
            graph.direction(left, right)
            continue
        raise Exception("Unexpected line '", line, '" found! Each line must list two nodes and give their relation as "<->", "<-", or "->"!')
    return graph


class GraphNode():
    def __init__(self, name):
        self.name = name
        self.connections = set()
    
    def connect(self, otherNode):
        self.connections.add(otherNode)


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


def suggestReplacements(tableName, constraints):
    replacements = [None for _ in range(len(constraints))]
    hasFile = dict()
    
    # Unfortunately, we need to map from the table columns used in constraints to the
    #  associated files, which cannot be an elegant solution.
    from src.domains import Domain
    if tableName == Domain.CAR:
        hasFile['condition'] = 'condition'
        hasFile['type'] = 'car-type'
        hasFile['paint_color'] = 'color'
        hasFile['state'] = 'us-states'
    elif tableName == Domain.FURNITURE:
        return replacements # No options for furniture :/
    elif tableName == Domain.HOUSING:
        return replacements # I could maybe match on suburb location?
    elif tableName == Domain.JEWELRY:
        hasFile['tags'] = 'material'
    elif tableName == Domain.JOB:
        hasFile['sector'] = 'work-sector'
        hasFile['location'] = 'us-states'
        pass
    elif tableName == Domain.MOTORCYCLE:
        return replacements # No options for motorcycles either :/
    
    filePrefix = "/../similarity/"
    # Building each graph takes a lot of work, which we don't want to do unless we need it
    graphs = dict()
    
    # Now we are going to go through each constraint and suggest potential alternatives
    for i in range(len(constraints)):
        changed = False
        # we will look for instances of ' LIKE ', which indicates that it is a type I or type II value
        constr = constraints[i]
        indx = constr.find(' LIKE "% ')
        while indx != -1:
            # we found an instance! Great, now we check if we can partial match on it
            breakIndex = indx - 1
            while breakIndex > -1:
                # go backwards until we either find a break or the beginning of the string
                if constr[breakIndex] == ' ' or constr[breakIndex] == '(':
                    break
                breakIndex -= 1
            attr = constr[breakIndex + 1:indx]
            if attr in hasFile:
                # Excellent! We found an attribute we can partial match on
                # We must build the graph if it has not been built already
                if not attr in graphs:
                    graph = createFromStringLines(readFileLines(filePrefix + hasFile[attr] + '.txt'))
                    graphs[attr] = graph # place it in the dictionary for next time
                else:
                    graph = graphs[attr]
                
                # try to find the node with value matching given value from the constraint
                end = constr.index(' %"', indx + 9)
                matchValue = constr[indx + 9:end]
                if matchValue in graph.nodes:
                    neighbors = graph.nodes[matchValue].connections
                    # Lastly, we build a giant OR with all the neighboring values 
                    #  (We don't exclude matchValue since it may be helpful to match
                    #  on with our liberal replacement strategy.)
                    newClause = '(' + attr + ' LIKE "% ' + matchValue + ' %"'
                    for neighbor in neighbors:
                        newClause += ' OR ' + attr + ' LIKE "% ' + neighbor.name + ' %"'
                    newClause += ')'
                    # Now we need to insert our new clause to replace what was there
                    constr = constr[:breakIndex + 1] + newClause + constr[end+3:]
                    
                    # Finally we want to calculate how many to skip ahead in the search
                    indx = constr.find(' LIKE "% ', breakIndex + len(newClause))
                    changed = True
                    continue
            
            indx = constr.find(' LIKE "% ', indx + 13) # 13 is length of pattern ' LIKE "% x %"'
        if changed: # leave the "replacement" as None if there were no partial-match changes
            replacements[i] = constr
    return replacements
