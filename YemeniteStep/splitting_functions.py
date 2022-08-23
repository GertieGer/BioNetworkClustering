import networkx as nx
from networkx.algorithms.community.centrality import girvan_newman
import evaluation
import normal_newman
import yemenitestep

# Classic Louvain
def louvainfunc(G, m=None, k=None):
    """
        Uses the Louvain heuristic from:
            Blondel, V.D. et al. Fast unfolding of communities in
        large networks. J. Stat. Mech 10008, 1 - 12(2008).
        
        If m,k are given - instead of treating the subgraph as independant,
        we use the k and m values (node degree and num of edges) from the super graph.
    """
    l = yemenitestep.Louvain(G)
    if k is not None:
        l.relative_m = m
        l.relative_ks = k
    l.run()
    return l.community_map

def louvain_random(G, m=None, k=None):
    """
        Same as Louvainfunc, but with randomization.
    """
    l = yemenitestep.Louvain(G, randomized=True)
    if k is not None:
        l.relative_m = m
        l.relative_ks = k
    l.run()
    return l.community_map

# Girvan-Newman (edge betweenes) - Maximise Modularity
def girvanNewmanMaxModularity(G, m=None, k=None):
    comps = girvan_newman(G)
    max_comp = None
    max_mod = -1
    for comp in comps:
        if k is None: mod = evaluation.modularity(G, comp) 
        else: mod = evaluation.relative_modularity(G, comp, m, k) 
        if mod>max_mod:
            max_mod = mod
            max_comp = comp
    
    return evaluation.arr_to_dic(max_comp)
    
# Girvan-Newman (edge betweenes) - Maximise Modularity
def girvanNewmanConductance(G):
    comps = girvan_newman(G)
    max_comp = None
    max_cond = -1
    for comp in comps:
        cond = evaluation.conductance(G, comp)
        if cond>max_cond:
            max_cond = cond
            max_comp = comp
    
    return evaluation.arr_to_dic(max_comp)

# Classical Newman (devide and conquer)
def newman(G):
    return normal_newman.partition(G)