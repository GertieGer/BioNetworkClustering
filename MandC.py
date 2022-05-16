

import networkx.algorithms.community as nx_comm


def mod(G,arr):
    m=nx_comm.modularity(G,arr)
    return m

def cond(G,arr):
    q=0
    for A in arr:
        T=arr.pop(A)
        q+=nx_comm.conductance(G,A,T)
    res=q/len(arr)
    res=1-res
    return res
        
        
    