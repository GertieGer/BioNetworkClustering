from communitytracker import CommunityTracker
import networkx as nx
from collections import defaultdict # TODO: remove, annoying
import random
import splitting_functions


class Louvain: 

    def __init__(self, G, splitting_func=None, verbose=False, randomized=False, remerge=False, relative=False):
        # SETTINGS
        self.splitting_func = splitting_func
        self.verbose = verbose
        self.randomized = randomized
        self.remerge = remerge
        self.pre_split_communities = None
        self.relative = relative
        # Create helper to track network statistics.
        # We use the coarse_grain_graph in the iterations.
        self.tracker = CommunityTracker()
        self.original_graph = G
        self.coarse_grain_graph = G
        # If this is running on a subgraph, these may be useful (when using 'relative' option)
        self.relative_ks = None
        self.relative_m = None
        # self.community_history keeps track of the community maps
        # from each iteration.
        self.community_history = []
        self.iteration_count = 0
        self.finished = False
        # Final community map and list of communities created at end.
        self.community_map = None
        self.communities = None
        
    def run(self):
        """Runs the iterations of the Louvain method until finished then
        generates the final community map.
        """
        i = 0
        while not self.finished:
            self.iterate()
            i+=1
        if self.verbose:
            print("Finished in {} iterations".format(self.iteration_count))
        self.community_map = self.generate_community_map(
            self.community_history)
        self.communities = self.invert_community_map(self.community_map)

    def iterate(self):
        """Performs one iteration of the Louvain method on the current graph G.
        For each node we move it to a neighbouring community which causes the
        greatest increase in modularity (if there is no such positive change we
        leave it where it is). We continue this until no more moves can be done
        so we have reached a local modularity optimum.
        We then create a new coarse grained graph where each node represents a
        community for the next iteration.
        """
        self.iteration_count += 1
        if self.verbose:
            print("Iteration: ", self.iteration_count)
        # modified if we have made at least one change overall.
        # improved if we have made at least one change in the current pass.
        modified = False
        improved = True
        G = self.coarse_grain_graph

        # Relative Option 
        if self.relative_ks is not None: # if k is given, meaning I am a subgraph
            self.tracker.initialize_network_statistics(G, self.relative_m, self.relative_ks)
        else:
            self.tracker.initialize_network_statistics(G)
        community_map = self.tracker.node_to_community_map

        # Remerging Option
        if self.remerge:
            self.remerge_communities(community_map)
 
        # Iteration
        while improved:
            improved = False

            nodes = G.nodes()

            # Random Option
            if self.randomized:
                nodes = list(G.nodes())
                random.seed()
                random.shuffle(nodes)

            for node in nodes:
                best_delta_Q = 0.0
                old_community = community_map[node]
                new_community = old_community
                
                neighbour_communities = self.get_neighbour_communities(
                    G, node, community_map) # Dict: {community:sum_of_weihgts_of_edges_to_community}

                # Isolate the current node and find the best neighbouring
                # community (including checking the original).
                
                old_incident_weight = neighbour_communities.get(
                    old_community, 0) # incident_weight = sum_of_weihgts_of_edges_to_community

                # Remove node from current community
                self.tracker.remove(node, old_community, old_incident_weight)

                # Try adding node to neighbor communities
                for community, incident_wt in neighbour_communities.items():
                    delta_Q = self.calculate_delta_Q(
                        G, node, community, incident_wt)
                    if delta_Q > best_delta_Q:
                        best_delta_Q = delta_Q
                        new_community = community

                # Move to the best community and check if we actually improved.
                new_incident_weight = neighbour_communities[new_community]
                self.tracker.insert(node, new_community, new_incident_weight)
                if self.verbose:
                    message = "Moved node {} from community {} to community {}"
                    print(message.format(node, old_community, new_community))

                if new_community != old_community:
                    improved = True
                    modified = True
            # End node loop
            
        # After no improvment has been made
        if modified:

            # Splitting function option
                # After Louvain's shot at finding communities, 
                # run a clustering method in each community to possibly split it even more
            if self.splitting_func is not None:
                self.communities = self.invert_community_map(community_map)
                self.split_communities(self.communities, community_map)

            self.relabel_community_map(community_map) # relabe remaining communities from 0,1..n
            self.community_history.append(community_map)
            # Generate new graph where each community is a node
            self.coarse_grain_graph = self.generate_coarse_grain_graph(
                G, community_map)
        else:
            # We didn't modify any nodes so we are finished.
            self.finished = True

    def remerge_communities(self, community_map):
        """
            Remerge Option:
            If the remerge option is on, sub-communities that used to be part of the same community
            (before running the internal spiltting functio) will be remerged so that they still
            become independent nodes in the coarse graph, but they will belong to same community 
            (as opposed to the usual "each node is it's own community")
        """
        if not self.pre_split_communities:
            return # nothing to remerge yet

        G = self.coarse_grain_graph
        nodes = G.nodes()
        head_of_pre_community= {}

        for node in nodes:
            # Since we are changing the communities of the nodes, we need to do it
            # in such a way the the community tracker is updated correctly

            # Remove node from  its current community
            curr_community = community_map[node]
            new_community = curr_community
            neighbour_communities = self.get_neighbour_communities(
                G, node, community_map)
            old_incident_weight = neighbour_communities.get(
                curr_community, 0)
            self.tracker.remove(node, curr_community, old_incident_weight)
            
            # Add node to the merged community
            pre_community = self.pre_split_communities[node]
            if pre_community in head_of_pre_community:
                new_community = community_map[head_of_pre_community[pre_community]] 
                # if pre communitiy has a node that represents it, ass this node to the cimmounity of that node
            else:
                # else, make this node the "head" that represents the pre-community
                head_of_pre_community[pre_community] = node

            new_incident_weight = neighbour_communities[new_community]
            self.tracker.insert(node, new_community, new_incident_weight)
            if self.verbose:
                message = "Moved node {} from community {} to community {}"
                print(message.format(node, curr_community, new_community))

    def split_communities(self, communities, community_map):
        """
        Applies a divisive clustering algorithm on the subgraph defined by each community
        in "communities" list. this may split the community to sub communities.
        """
        max_community = 0
        new_community_map = community_map.copy()
        for i, community in enumerate(communities):
            if len(community)<10: ## CHANGED FOR DEBUGING ##
                #to small
                for node in community:
                    new_community_map[node] = max_community
                max_community += 1
                continue
            subgraph = (self.coarse_grain_graph).subgraph(community)

            if self.relative:
                # Please use the "relative" flag only if splitting_func supports that options
                sub_community_map = self.splitting_func(subgraph, self.tracker.m, self.tracker.degrees)
            else:
                sub_community_map = self.splitting_func(subgraph)

            sub_count = len(set(sub_community_map.values()))
            if len(sub_community_map.keys()) == sub_count:
                # not useful, ignore
                for node in sub_community_map:
                    new_community_map[node] = max_community
                max_community += 1
                continue

            else:
                for node, sub in sub_community_map.items():
                    new_community = max_community + sub
                    new_community_map[node] = new_community
                max_community += sub_count

        # after finding splitting dictionary, acctualy split the nodes
        self.reorder_communities(new_community_map, community_map)
    
    def reorder_communities(self, new_community_map, community_map):
        """
        This function is called at the end of split_communities().
        After running the splitting function, community_map now holds a new way to cluster the nodes.
        In this function we move the nodes to the communities suggested in the community_map,
        in a way that updates the community tracker.
        """
        G = self.coarse_grain_graph
        nodes = G.nodes()

        self.pre_split_communities = {}
        head_of_community= {}
        for node in nodes:
            curr_community = community_map[node]
            suggested_comm = new_community_map[node]
            if not suggested_comm in head_of_community:
                home = self.tracker.home_community_map[node]
                head_of_community[suggested_comm] = home # the original home of this node will be the new community for this node's sub
                self.pre_split_communities[home] = curr_community # so we know this new sub community once belonged to curr_community, which holds the community that louvain iteration found
            new_community = head_of_community[suggested_comm] 

            neighbour_communities = self.get_neighbour_communities(
                G, node, community_map)
            # Isolate the current node and find the best neighbouring
            # community (including checking the original).
            old_incident_weight = neighbour_communities.get(
                curr_community, 0)
            self.tracker.remove(node, curr_community, old_incident_weight)

            # Move to the best community and check if we actually improved.
            new_incident_weight = neighbour_communities[new_community]
            self.tracker.insert(node, new_community, new_incident_weight)

    def get_neighbour_communities(self, G, node, community_map):
        """Returns a dictionary with the neighbouring communities as keys and
        incident edge weights between node and the community as values.
        """
        neighbour_communities = defaultdict(int)
        for neighbour in G[node]:
            if neighbour != node:
                neighbour_community = community_map[neighbour]
                w = G[node][neighbour].get("weight", 1)
                neighbour_communities[neighbour_community] += w
        return neighbour_communities

    def calculate_delta_Q(self, G, node, community, incident_weight):
        """Calculate change in modularity from adding isolated node to
        community."""
        # Sum of the weights of the links incident to nodes in C.
        sigma_tot = self.tracker.community_degrees[community]
        # Sum of the weights of the links incident to node i.
        k_i = self.tracker.degrees[node]
        # Sum of the weights of the links from i to nodes in C.
        k_i_in = incident_weight
        # Sum of the weights of all the links in the network.
        m = self.tracker.m

        delta_Q = 2 * k_i_in - sigma_tot * k_i / m
        return delta_Q

    def generate_coarse_grain_graph(self, G, community_map):
        """Generates new coarse grain graph with each community as a single
        node.
        Weights between nodes are the sum of all weights between respective
        communities and self loops are added for the weights of he internal
        edges.
        In case G is a subgraph of some bigger graph, k_i may not be equal to degree, so ks are also calaulated.
        """
        new_graph = nx.Graph()
        new_ks = {}
        # Create nodes for each community.
        for community in set(community_map.values()):
            new_graph.add_node(community)
            new_ks[community] = 0

        # Create the combined edges from the individual old edges.
        for u, v, w in G.edges(data="weight", default=1):
            c1 = community_map[u]
            c2 = community_map[v]
            new_weight = w
            if new_graph.has_edge(c1, c2):
                new_weight += new_graph[c1][c2].get("weight", 1)
            new_graph.add_edge(c1, c2, weight=new_weight)

        # Relative Option: Update ks for new nodes        
        if self.relative_ks:
            for node in community_map:
                new_ks[community_map[node]] += self.relative_ks[node]
            self.relative_ks = new_ks

        return new_graph

    def relabel_community_map(self, community_map):
        """Relabels communities to be from 0 to n."""
        orig = community_map.copy()
        community_labels = set(community_map.values())
        new_pre_split_communities = {}
        relabelled_communities = {j: i for i, j in enumerate(community_labels)}
        for node in community_map:
            community = community_map[node]
            community_map[node] = relabelled_communities[community]
            if self.pre_split_communities is not None:
                new_pre_split_communities[relabelled_communities[community]] = \
                    self.pre_split_communities[community]
                
        
        if self.pre_split_communities is not None:
            self.pre_split_communities = new_pre_split_communities

    def invert_community_map(self, community_map):
        """Inverts a community map from nodes to communities to a list of
        lists of nodes where each list of nodes represents one community.
        """
        inverted_community_map = defaultdict(list)
        for node in community_map:
            inverted_community_map[community_map[node]].append(node)
        return list(inverted_community_map.values())

    def generate_community_map(self, community_history):
        """Builds the final community map using the history of iterations."""
        community_map = {node: node for node in self.original_graph}
        for node in community_map:
            for iteration in community_history:
                # Follow iterations to find final community of node.
                community_map[node] = iteration[community_map[node]]
        return community_map


def get_communities(G, splitting_func=None, verbose=False, randomized=False, remerge=False, relative=False):
    """
        The YemmeniteStep method:
        
        This methods implements the Louvain method, with an additional step of running 
        an additional clustering algorithm (reffered to here as splitting functions) on each community Louvaine finds,
        at each iteration (just before generating the new coarse graph).

        We offer these options for the inner splitting functions:
            1. "Louvain"
                The Louvain Method (supports 'relative' option)
            2. "GN_modularity"
                The Girvan-Newman method, maximizng modularity (supports 'relative' option)
            3. "GN_conductance" 
                The Girvan-Newman method, maximizng conductance
            4. "Newman"
                The 'Divide and conquer' Newamn method.
            
        We offer these additional options:
            1. randomized
                Randomizes the order in which Louvain iterates through nodes on
            2. remerge
                After splitting a community into sub-communities, if 'remerge' option is selected
                then in the coarse graph; sub-nodes will belong to the same community.
            3. relative
                if this option is selected, the values of k (node degree) and m (num of edeges) in each
                sub-graph will be same as in the super-graph.
                only "Louvain" and "GN-modularity" support this option.
    """
    if isinstance(splitting_func, str):   
        if splitting_func == "Louvain":
            if randomized:
                splitting_func = splitting_functions.louvain_random
            else:
                splitting_func = splitting_functions.louvainfunc

        elif splitting_func == "GN_modularity":
            splitting_func = splitting_functions.girvanNewmanMaxModularity

        elif splitting_func == "GN_conductance":
            if relative:
                print("Sorry, 'GN_conductance' does not support 'relative' option")
            else:
                splitting_func = splitting_functions.girvanNewmanConductance

        elif splitting_func == "Newman":
            if relative:
                print("Sorry, 'Newman' does not support 'relative' option")
            else:
                splitting_func = splitting_functions.newman

    louvain = Louvain(G, verbose=verbose, randomized=randomized, splitting_func=splitting_func, remerge=remerge, relative=relative)
    louvain.run()
    return louvain.communities

# def detect_communities(G, verbose=False, randomized=False, splitting_func=None, remerge=False):
#     """Returns the detected communities as a list of lists of nodes
#     representing each community.
#     Uses the Louvain heuristic from:
#         Blondel, V.D. et al. Fast unfolding of communities in
#     large networks. J. Stat. Mech 10008, 1 - 12(2008).
#     """
#     louvain = Louvain(G, verbose=verbose, randomized=randomized, splitting_func=splitting_func, remerge=remerge)
#     louvain.run()
#     return louvain.communities, louvain.community_map

def louvainfunc(G, verbose=False, randomized=False, splitting_func=None, remerge=False):
    louvain = Louvain(G, verbose=False, randomized=False, splitting_func=None, remerge=False)
    louvain.run()
    return louvain.community_map