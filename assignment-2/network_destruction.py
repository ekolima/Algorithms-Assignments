import argparse
from collections import deque

#creategraph:
#*input* a txt file containing all the edges of the graph (start and terminal node)
#*output* the graph in a dictionary data structure where keys are all nodes and values the adjacency list for each node
def creategraph(filename):
    g = {}
    with open(filename) as graph:
        for line in graph:
            if int(line.split()[0]) not in g:
                g[int(line.split()[0])] = []
            if int(line.split()[1]) not in g:
                g[int(line.split()[1])] = []
            g[int(line.split()[0])].append(int(line.split()[1]))
            g[int(line.split()[1])].append(int(line.split()[0]))
    return g

#degreeremoval: removes certain number of nodes from a graph, based on their degree
#*input* graph (as it is created by the creategraph method), the number of nodes to be removed
#*output* list with all the removed nodes and their degree
def degreeremoval(graph,num_nodes):
    c=0
    removed=[]

    while (c < num_nodes):
        maxdegree = max([len(graph[i]) for i in graph])
        node = min([int(i) for i in graph if len(graph[i]) == maxdegree])

        removed.append([node,maxdegree])
        graph.pop(node)

        for i in graph:
            for j in graph[i]:
                if j == node:
                    graph[i].remove(node)
        c=c+1
    return removed

#collectiveinfluence: removes certain number of nodes from a graph, based on their collective influence
#*input* graph (as it is created by the creategraph method), radius of influence (r), the number of nodes to be removed
#*output* list with all the removed nodes and their collective influence
def collectiveinfluence(graph,r,num_nodes):
    c=0
    removed=[]
    influences={}
    for i in graph:
        influences[i]=(len(graph[i])-1)*ball(i,graph,r)

    while (c < num_nodes):
        maxinfl = max([influences[i] for i in influences])
        node = min([i for i in influences if (influences[i] == maxinfl)])

        removed.append([node,maxinfl])
        dst=bfs(graph,node)
        dst.pop(node)
        graph.pop(node)
        influences.pop(node)

        for i in graph:
            for j in graph[i]:
                if j == node:
                    graph[i].remove(node)
        for i in dst:
            if dst[i] <= r+1:
                influences[i]=(len(graph[i])-1)*ball(i,graph,r)
        c=c+1
    return removed

#ball: calculates the sum of (kj-1) for each j that its distance from a certain node is equal to the radius r
#*input* node to calculate distances from, graph (as created from creategraph), radius r
#*output* sum(kj-1), where dist(ij)=r
def ball(node,graph,r):
    infl=0
    dist=bfs(graph,node)
    infl = sum([len(graph[j])-1 for j in dist if dist[j] == r])
    return infl

#bfs: performs breadth-first search (bfs) to calculate distances between a node and all other nodes if the graph
#*input* graph (as created from creategraph), node to calculate distances from
#*output* a dictionary containing all nodes as keys and their distance from the given node, as values
def bfs(graph,node):
    q = deque()
    visited={}
    inqueue={}
    distances={}

    for i in graph:
        visited[i]=False
        inqueue[i]=False
    q.appendleft(node)
    inqueue[node] = True
    counter = 0
    distances[node]=counter

    while not (len(q) == 0):
        c = q.pop()
        inqueue[c] = False
        visited[c] = True
        counter=counter+1

        for v in graph[c]:
            if not(visited[v] or inqueue[v]):
                distances[v]=min(counter,min([(distances[z]+1) for z in graph[v] if z in distances]))
                q.appendleft(v)
                inqueue[v] = True
    return distances

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--method", action="store_true")
    parser.add_argument("-r", "--radius", type=int, help="give radius")
    parser.add_argument("num_nodes", type=int, help="give number of nodes")
    parser.add_argument("input_file", help="give file name")

    args = parser.parse_args()
    method = args.method
    num_nodes = args.num_nodes
    file = args.input_file
    if args.radius:
        radius = args.radius

    graph = creategraph(file)

    if method:
        c = degreeremoval(graph,num_nodes)
    else:
        c = collectiveinfluence(graph,radius,num_nodes)
    for i in c:
        print(i[0],i[1]) #alternative: print(*i)

main()
