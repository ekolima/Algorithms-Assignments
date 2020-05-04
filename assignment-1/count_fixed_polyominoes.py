import argparse
import pprint

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--print", action="store_true")
parser.add_argument("polsize", type=int, help="polyominoes size")

args = parser.parse_args()
size = args.polsize

#to create the graph I noticed that the most open/sparse polyominoes (so the worse case scenario) would have a pyramid shape
#like the one in the assignment (for the pentomino) and this would be the case for any given n. Thus, I generalised this "rule"
#to create the square lattice and the graph for any given n.
def createGraph(size):
    g={}
    #generate all nodes
    listofnodes=[]
    for i in range(0,int(size)):
        for j in range(0,int(size)-i):
            listofnodes.append((i,j))
            if (i != 0 and j != 0):
                listofnodes.append((-i,j))
    #separate the nodes
    for i in range(int(min([i[0] for i in listofnodes])),int(size)):
        for j in listofnodes:
            if j[0] == i:
                g[j]=[]
    #create values - the neighbours of each node
    for i in g:
        toadd=[]
        if (i[0]+1,i[1]) in g:
            toadd.append((i[0]+1,i[1]))
        if (i[0],i[1]+1) in g:
            toadd.append((i[0],i[1]+1))
        if (i[0]-1,i[1]) in g:
            toadd.append((i[0]-1,i[1]))
        if (i[0],i[1]-1) in g:
            toadd.append((i[0],i[1]-1))
        g[i]=toadd
    return g

#input: graph, untried list of nodes, size of polyomino, current polymino, counter
def cfp(g,untried,n,p,c):
    while (untried != set()):
        u = untried.pop()
        p.append(u)
        if (len(p) == n):
            c+=1
        else:
            nei = set()
            for v in g[u]:
                if (v not in untried) and (v not in p):
                    #pu: adj list of p\u --> nu: values of keys in pu (p\u)
                    pu={x for x in p if x != u}
                    nu=set()
                    for i in pu:
                        for j in g[i]:
                            nu.add(j)
                    if (v not in nu):
                        nei.add(v)
            newuntr = untried.union(nei)
            c=cfp(g,newuntr,n,p,c)
        p.remove(u)
    return c

def printpolys(printq, graph, count):
    if printq:
        pprint.pprint(graph)
    print(count)

g = createGraph(size)
c = cfp(g,{(0, 0)},size,[],0)
printpolys(args.print,g,c)
