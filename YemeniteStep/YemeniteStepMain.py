"""
~~~ The YemmeniteStep method ~~~

This methods implements the Louvain method, with an additional step of running 
an additional clustering algorithm (reffered to here as splitting functions) on each community Louvaine finds,
at each iteration (just before generating the new coarse graph).

* We offer these options for the inner splitting functions:
    1. "Louvain"
        The Louvain Method (supports 'relative' option)
    2. "GN_modularity"
        The Girvan-Newman method, maximizng modularity (supports 'relative' option)
    3. "GN_conductance" 
        The Girvan-Newman method, maximizng conductance
    4. "Newman"
        The 'Divide and conquer' Newamn method.
    
* We offer these additional options:
    1. randomized
        Randomizes the order in which Louvain iterates through nodes on
    2. remerge
        After splitting a community into sub-communities, if 'remerge' option is selected
        then in the coarse graph; sub-nodes will belong to the same community.
    3. relative
        if this option is selected, the values of k (node degree) and m (num of edeges) in each
        sub-graph will be same as in the super-graph.
        only "Louvain" and "GN-modularity" support this option.

* How To Use:
  get_communities(G, splitting_func=None, verbose=False, randomized=False, remerge=False, relative=False)

  Parameters:
    - G: NetworkX graph
    - splitting_func: string, function, or None
        Use one of the strings from the list of splitting functions above,
        or pass your own function. If None, regular Louvain will be implemented.
    - verbose: boolean or None
        If True, prints some comments
    - randomized: boolean or None
        If True, randomized option will be used.
    - remerge: boolean or None
        If True, remerge option will be used.
    - relative: boolean or None
        If True, relative option will be used.
        only "Louvain" and "GN-modularity" support this option.

    Returns:
        A list of sets (partition of G). 
        Each set represents one community and contains all the nodes that constitute it.

* Example:

>>> import networkx as nx
>>> import yemenitestep as ys
>>>
>>> G = nx.karate_club_graph()
>>> ys.get_communities(G, splitting_func="GN_modularity", relative=True)
[[0, 1, 2, 3, 7, 11, 12, 13, 17, 19, 21], [4, 5, 6, 10, 16], [8, 9, 14, 15, 18, 20, 22, 26, 29, 30, 32, 33], [23, 24, 25, 27, 28, 31]]

"""

from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import networkx as nx
import scipy
import sys
import os
import time
from datetime import datetime
import evaluation
from threading import Thread
import yemenitestep as ys




def get_comms_from_dic(community_map):
    inverted_community_map = defaultdict(list)
    for node in community_map:
        inverted_community_map[community_map[node]].append(node)
    return list(inverted_community_map.values())


def get_comm_dic(path):
    d = {}
    f = open(path, "r")
    lines = f.readlines()
    for line in lines:
        node, comm = line.strip().split()
        d[int(node)] = int(comm)
    return d



n_vals = [1000, 10000]
mu_vals = (0.4, 0.5, 0.6)
num_of_benchmarks = 10
now = datetime.now()
dt_string = now.strftime("%d_%m_%Y__%H_%M")
methods_to_test = [
    "Louvain",
    "GN_modularity",
    "GN_conductance",
    #"Newman",
]
RANDOMIZED = True
REMERGE = False
RELATIVE = True
network = f"1000_0.4_0"
netPath = sys.path[0]+r"\..\Graphs\{0}\network.dat"
commPath = sys.path[0]+r"\..\Graphs\{0}\community.dat"

netfile = netPath.format(network)
real_comms = get_comm_dic(commPath.format(network))
G = nx.read_edgelist(netfile, nodetype=int)

dic = ys.get_communities(G, splitting_func="Louvain", randomized=RANDOMIZED, remerge=REMERGE ,relative=RELATIVE)
print(dic)