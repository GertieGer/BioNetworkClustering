
# The YemmeniteStep Method Python Project
==============================

This module implements community detection.
The Yemmenite Step Method implements the Louvain method [#]_, with an additional step of running an additional clustering algorithm (reffered to here as splitting functions) on each community Louvaine finds, at each iteration (just before generating the new coarse graph).

* We offer these options for the inner splitting functions:
    1) "Louvain"__
        The Louvain Method (supports 'relative' option)
    2) "GN_modularity"__
        The Girvan-Newman method, maximizng modularity (supports 'relative' option)
    3) "GN_conductance"__
        The Girvan-Newman method, maximizng conductance
    4) "Newman"__
        The 'Divide and conquer' Newamn method.
    
* We offer these additional options:
    1) randomized
        Randomizes the order in which Louvain iterates through nodes on
    2) remerge
        After splitting a community into sub-communities, if 'remerge' option is selected
        then in the coarse graph; sub-nodes will belong to the same community.
    3) relative
        if this option is selected, the values of k (node degree) and m (num of edeges) in each
        sub-graph will be same as in the super-graph.
        only "Louvain" and "GN-modularity" support this option.

### Requirements
------------

* Python 3
* NetworkX 1.11


### Getting Started
-----
Install the package using::

    python setup.py install

### Usage
-----
```
communities = get_communities(G, splitting_func=None, verbose=False, randomized=False, remerge=False, relative=False)
```

###### Parameters:
* **G**: *NetworkX graph*__
* **splitting_func**: *string, function, or None*__
    Use one of the strings from the list of splitting functions above,
    or pass your own function. If None, regular Louvain will be implemented.
* **verbose**: *boolean or None*__
    If True, prints some comments
* **randomized**: *boolean or None*__
    If True, randomized option will be used.
* **remerge**: *boolean or None*__
    If True, remerge option will be used.
* **relative**: *boolean or None*__
    If True, relative option will be used.
    only "Louvain" and "GN-modularity" support this option.

###### Returns:
    A list of sets (partition of G). 
    Each set represents one community and contains all the nodes that constitute it.

### Examples
-----
```

    import networkx as nx
    import yemenitestep as ys

    G = nx.karate_club_graph()
    partition =  ys.get_communities(G, splitting_func="GN_modularity", relative=True)
    > [[0, 1, 2, 3, 7, 11, 12, 13, 17, 19, 21], [4, 5, 6, 10, 16], [8, 9, 14, 15, 18, 20, 22, 26, 29, 30, 32, 33], [23, 24, 25, 27, 28, 31]]

```

References
----------

.. [#] Blondel V.D., Guillaume J.-L., Lambiotte R., Lefebvre E. (2008) Fast
   unfolding of communities in large networks. J. Stat. Mech. P10008
   (https://arxiv.org/abs/0803.0476)
