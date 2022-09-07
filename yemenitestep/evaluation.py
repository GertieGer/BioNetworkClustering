import networkx.algorithms.community as nx_comm
import networkx as nx
from itertools import product
import math

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

def intersection_size(a, b):
    return len(set(a).intersection(set(b)))

def accuracy(annotated_complexes, candidate_clusters):
    """
    Using notations from "Evaluation of clustering algorithms for protein-protein interaction networks, Brohee & van Helden, BMC Bioinformatics, 2006".
    """
    ppv = PPV(annotated_complexes, candidate_clusters)
    sn = sensitivity(annotated_complexes, candidate_clusters)
    return math.sqrt(sn*ppv)

def sensitivity(annotated_complexes, candidate_clusters):
    sum_of_max_intersections = 0
    sum_of_all_lens = 0
    
    # for each complex, 
    for annotated_complex in annotated_complexes:
        max_int_with_complex = 0
        # find best matching cluster
        for candidate_cluster in candidate_clusters:
            int_size = intersection_size(annotated_complex, candidate_cluster)
            max_int_with_complex = max(int_size, max_int_with_complex)

        sum_of_max_intersections += max_int_with_complex
        sum_of_all_lens += len(annotated_complex) # Ni

    if sum_of_all_lens>0:
        return sum_of_max_intersections/sum_of_all_lens
    return 0

def PPV(annotated_complexes, candidate_clusters):
    sum_of_max_intersections = 0
    sum_of_all_intersections = 0 # sum_i(T_.j)
    
    # for each cluster
    for candidate_cluster in candidate_clusters:
        max_int_with_cluster = 0
        # find best matching complex
        for annotated_complex in annotated_complexes:
            # and also calculate "T_.j", which is the sum of Tij for all i (where j is the cluster and i is a complex)
            int_size = intersection_size(annotated_complex, candidate_cluster)
            sum_of_all_intersections += int_size

            max_int_with_cluster = max(int_size, max_int_with_cluster)
        sum_of_max_intersections += max_int_with_cluster
            
    if sum_of_all_intersections>0:
        return sum_of_max_intersections/sum_of_all_intersections
    return 0





