# Example:

import yemenitestep.yemenitestep as ys
from yemenitestep import evaluation
import networkx as nx

# Create a NetworkX graph
G = nx.karate_club_graph()

# If you have a known solution:
real_communities =[[0, 1, 2, 3, 7],[11, 12, 13, 17, 19, 21], [4, 5, 6, 10, 16], [8, 9, 14, 15, 18], [20, 22, 26, 29, 30, 32, 33], [23, 24, 25, 27, 28, 31]]

# Run Yemenite Step with GN Modularity as a splitting function, and Relative option 
communities =  ys.get_communities(G, splitting_func="GN_modularity", relative=True)

# Evaluate the clustering
modularity = evaluation.modularity(G, communities)
conductance = evaluation.conductance(G, communities)
jaccard = evaluation.jaccard(real_communities, communities) # can also get community dicts as input
# accuracy = evaluation.accuracy(annotated_complexes, communities)

print(f"""
This example file runs:
YemenStep with the Girvan-Newman (Modularity) as the splitting method,
with the additional option "Relative",
on LFR_benchmark_graph(100, 3, 1.5, 0.4).

The communities found are:
{communities}

Modularity = {modularity}
Conductance = {conductance}
Jaccard = {jaccard}
""")
