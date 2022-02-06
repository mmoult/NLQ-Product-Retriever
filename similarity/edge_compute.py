from src.content_match import SimilarityGraph, readFileLines, createFromStringLines, outputToFile

def expandFile(graph, filePath):
    # We are going to expand the file using the Floyd-Warshall algorithm to find the shortest path between
    #  each of the nodes.
    import math
    
    # We need to create a 2D matrix that is V * V, where V is the number of nodes in the graph
    shortest = [[math.inf for _ in graph.nodes] for _ in graph.nodes]
    # Then we need to add all edges to the matrix appropriately
    numberedNodes = dict() # We store the index number of all nodes for faster lookup
    
    numNodes = len(graph.nodes)
    nodes = list(graph.nodes.values())
    for i in range(numNodes):
        node = nodes[i]
        numberedNodes[node] = i
        for connect in node.connections:
            if connect.toNode not in numberedNodes:
                # keep looking until we find the referenced node
                j = i + 1
                while j < len(graph.nodes):
                    if nodes[j] is connect.toNode:
                        numberedNodes[connect.toNode] = j
                        break
                    j += 1
                else:
                    # the node could not be found!
                    # Currently, we will simply ignore it
                    continue
            to = numberedNodes[connect.toNode]
            shortest[i][to] = connect.cost
    
    # Now that all the data has been added into our matrix, we can begin
    #  Floyd-Warshall's algorithm
    # Note that self-loops don't make any sense in this context, so they
    #  are summarily skipped
    numNodes = len(graph.nodes)
    for k in range(numNodes):
        for i in range(numNodes):
            if k == i:
                continue
            
            for j in range(numNodes):
                if k == j or i == j:
                    continue
                
                shortest[i][j] = min(shortest[i][j],
                                     shortest[i][k] + shortest[k][j])
    
    # Lastly, we need to print our results out to the file
    # We will create a new graph from the matrix, then use the utility
    #  provided by the content_match module to do it.
    newGraph = SimilarityGraph()
    for tail in range(numNodes):
        tailName = nodes[tail].name
        for head in range(numNodes):
            if tail == head:
                continue # no self-loops!
            if shortest[tail][head] != math.inf:
                newGraph.direction(nodes[head].name, tailName, shortest[tail][head])
    outputToFile(newGraph, filePath)


if __name__ == '__main__': # Specify a file to fill out edges for with command line arg
    import sys
    if len(sys.argv) != 2:
        print("Specify the file path to analyze!")
    else:
        path = sys.argv[1]
        lines = readFileLines(path)
        graph = createFromStringLines(lines)
        expandFile(graph, path)
