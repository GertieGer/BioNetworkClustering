
The Yemmenite Step Method Python Project
==============================

This module implements community detection using the Yemmenite Step Method.
The Yemmenite Step Method implements the Louvain method [#f1]_ , with an additional step of running an additional clustering algorithm (reffered to here as splitting functions) on each community Louvaine finds, at each iteration (just before generating the new coarse graph).

| We offer these options for the inner splitting functions
1. Louvain
    The Louvain Method (supports 'relative' option)
2. GN_modularity
    The Girvan-Newman method [#f2]_, maximizng modularity (supports 'relative' option)
3. GN_conductance [#f1]_
    The Girvan-Newman method [#f2]_, maximizng conductance
4. Newman
    The 'Divide and conquer' Newamn method [#f3]_.
    
| We offer these additional options
1) Randomized
    Randomizes the order in which Louvain iterates through nodes on
2) Remerge
    After splitting a community into sub-communities, if 'remerge' option is selected
    then in the coarse graph; sub-nodes will belong to the same community.
3) Relative
    if this option is selected, the values of k (node degree) and m (num of edeges) in each
    sub-graph will be same as in the super-graph.
    only "Louvain" and "GN-modularity" support this option.

Requirements
------------

* Python 3
* NetworkX 1.11
* SciPy 0.9.0 


Getting Started
-----
Clone the repository::

    git clone https://github.com/GertieGer/BioNetworkClustering.git
    cd BioNetworkClustering

Install the package using::

    sudo python3 setup.py build
    sudo python3 setup.py install

Usage
-----
After Insatlling, you can import the package and call ys.get_communities() function:

.. code:: python

    import yemenitestep.yemenitestep as ys
    import networkx as nx

    G = nx.karate_club_graph()
    partition =  ys.get_communities(G, splitting_func="GN_modularity", relative=True)
    >> [[0, 1, 2, 3, 7, 11, 12, 13, 17, 19, 21], [4, 5, 6, 10, 16], [8, 9, 14, 15, 18, 20, 22, 26, 29, 30, 32, 33], [23, 24, 25, 27, 28, 31]]

You can Try running the example file from terminal::

    python3 YemeniteStepExample.py

Or Edit it to run different methods on any network you wish.
You can read the files in "Test Files", that were used for personal testing, but have examples on how to evaluate the methods using the evaluation methods in evaluation.py file.

get_communities Parameters:
-------------------

* G: ``NetworkX graph``
* splitting_func: ``string, function, or None*``
    Use one of the strings from the list of splitting functions above,
    or pass your own function. If None, regular Louvain will be implemented.
* verbose: ``boolean or None``
    If True, prints some comments
* randomized**: ``boolean or None``
    If True, randomized option will be used.
* remerge: ``boolean or None``
    If True, remerge option will be used.
* relative: ``boolean or None``
    If True, relative option will be used.
    only "Louvain" and "GN-modularity" support this option.

**Returns:**
A list of list (partition of G). 
Each list represents one community and contains all the nodes that constitute it.


References
----------

.. [#f1] Blondel V.D., Guillaume J.-L., Lambiotte R., Lefebvre E. (2008) Fast unfolding of communities in large networks. J. Stat. Mech. P10008 (https://arxiv.org/abs/0803.0476)
.. [#f2] Girvan M. and Newman M. E. J., Community structure in social and biological networks, Proc. Natl. Acad. Sci. USA 99, 7821–7826 (2002)
.. [#f3] Modularity and Community Structure in Networks M.E.J Newman, PNAS 2006
