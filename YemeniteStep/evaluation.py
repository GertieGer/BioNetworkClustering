import networkx.algorithms.community as nx_comm
import networkx as nx
from itertools import product

# Modularity ## TODO: Delete, useless
def modularity(G,arr):
    m=nx_comm.modularity(G,arr) 
    return m

# Modularity
def relative_modularity(G, partition, m, k):
    Q = 0
    for community in partition:
        for u, v in product(community, repeat=2):
            try:
                w = G[u][v].get("weight", 1)
            except KeyError:
                w = 0
            if u == v:
                # Double count self-loop weight.
                w *= 2
            Q += w - k[u] * k[v] / (2 * m)
    return Q / (2 * m)

# Conductance
def conductance(G,arr):
    q=0
    for A in arr:
        #T=arr.pop(A)
        T=G.nodes()-A
        q+=nx.conductance(G,A,T)
    res=q/len(arr)
    res=1-res
    return res
        
# Accurracy
def accurracy(G,arr): # TODO: check if correct...
    m=0
    N=0
    I=0
    m2=0
    N2=0
    for A in arr:
        m=0
        for B in arr:
            if (A!=B):
                h= A.intersection(B)
                if(m<len(h)):
                    m=len(h)
                    m2=len(B)
        N+=len(A)
        I+=m
        N2+=m2
    sen=I/N
    p=I/N2
    res=sen*p
    res=res**0.5
    return res

# Jaccard
def jaccard(X, Y):
    """ X - known solution, Y - suggested"""
    N11 = 0 # same cluster in both
    N00 = 0 # diff cluster in both
    N10 = 0 # same in X diff in Y
    N01 = 0 # diff in X same in Y

    nodes = X.keys()
    for i in nodes:
        for j in nodes:
            if j<=i:
                continue
            if X[i]==X[j]:
                if Y[i]==Y[j]:
                    N11+=1
                else:
                    N10+=1
            else:
                if Y[i]==Y[j]:
                    N01+=1
                else:
                    N00+=1

    return N11/(N10+N01+N11)

def arr_to_dic(arr):
    d={}
    for i, com in enumerate(arr):
        for node in com:
            d[node]=i
    return d

        
        
