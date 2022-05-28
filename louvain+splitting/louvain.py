# Tested on NetworkX 1.11
from communitytracker import CommunityTracker

import networkx as nx

from collections import defaultdict
import random


class Louvain:

    def __init__(self, G, verbose=False, randomized=False, splitting_func=None, remerge=False):
        # SETTINGS
        self.verbose = verbose
        self.randomized = randomized
        # Create helper to track network statistics.
        # We use the coarse_grain_graph in the iterations.
        self.tracker = CommunityTracker()
        self.original_graph = G
        self.coarse_grain_graph = G
        # self.community_history keeps track of the community maps
        # from each iteration.
        self.community_history = []
        self.iteration_count = 0
        self.finished = False
        # Final community map and list of communities created at end.
        self.community_map = None
        self.communities = None
        self.splitting_func = splitting_func
        self.remerge = remerge
        self.pre_split_communities = None

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
        #print("num of iterations: ", i)

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
        self.tracker.initialize_network_statistics(G)
        # name = "girvan_"+str(self.iteration_count) if self.splitting_func else "louvain_"+str(self.iteration_count)
        # gpath = "C:\\Users\\sabam\\OneDrive - mail.tau.ac.il\\Biological Networks\\"+name+".edges"
        # nx.write_weighted_edgelist(G, gpath)
        

        community_map = self.tracker.node_to_community_map
        if self.remerge:
            self.remerge_communities(community_map)

        while improved:
            improved = False

            nodes = G.nodes()
            if self.randomized:
                nodes = list(G.nodes())
                random.seed()
                random.shuffle(nodes)

            for node in nodes:
                best_delta_Q = 0.0
                old_community = community_map[node]
                new_community = old_community
                neighbour_communities = self.get_neighbour_communities(
                    G, node, community_map)
                # Isolate the current node and find the best neighbouring
                # community (including checking the original).
                old_incident_weight = neighbour_communities.get(
                    old_community, 0)
                self.tracker.remove(node, old_community, old_incident_weight)
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

        if modified:
            if self.splitting_func != None:
                # split community_map 
                self.communities = self.invert_community_map(community_map)
                self.split_communities(self.communities, community_map) # makes changes in community_map
            self.relabel_community_map(community_map)
            self.community_history.append(community_map)
            self.coarse_grain_graph = self.generate_coarse_grain_graph(
                G, community_map)
        else:
            # We didn't modify any nodes so we are finished.
            self.finished = True

    def remerge_communities(self, community_map):
        # maybe not the most efficient but this uses used code to remerge the nodes
        if not self.pre_split_communities:
            return # nothing to remerge yet

        G = self.coarse_grain_graph
        nodes = G.nodes()
        head_of_pre_community= {}

        for node in nodes:
            curr_community = community_map[node]
            new_community = curr_community
            neighbour_communities = self.get_neighbour_communities(
                G, node, community_map)
            # Isolate the current node and find the best neighbouring
            # community (including checking the original).
            old_incident_weight = neighbour_communities.get(
                curr_community, 0)
            self.tracker.remove(node, curr_community, old_incident_weight)
            
            pre_community = self.pre_split_communities[node]
            if pre_community in head_of_pre_community:
                new_community = community_map[head_of_pre_community[pre_community]] 
                # if pre communitiy has a node that represents it, ass this node to the cimmounity of that node
            else:
                # else, make this node the "head" that represents the pre-community
                head_of_pre_community[pre_community] = node

            # Move to the best community and check if we actually improved.
            new_incident_weight = neighbour_communities[new_community]
            self.tracker.insert(node, new_community, new_incident_weight)
            if self.verbose:
                message = "Moved node {} from community {} to community {}"
                print(message.format(node, curr_community, new_community))

    def reorder_communities(self, new_community_map, community_map):
        # maybe not the most efficient but this uses used code to remerge the nodes
        # after running the splitting function, community_map now holds a new way to cluster the nodes
        # however editing the community_map isn't enough, we need to actualy move the nodes to where they belong
        # so this function does that, moves nodes to theyer new location 

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

    def split_communities(self, communities, community_map):
        """by us:
        Applies a divisive clustering algorithm on the subgraph defined by each community.
        this may split the community to sub communities.
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
        return

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
        """
        new_graph = nx.Graph()
        # Create nodes for each community.
        for community in set(community_map.values()):
            new_graph.add_node(community)
        # Create the combined edges from the individual old edges.
        for u, v, w in G.edges(data="weight", default=1):
            c1 = community_map[u]
            c2 = community_map[v]
            new_weight = w
            if new_graph.has_edge(c1, c2):
                new_weight += new_graph[c1][c2].get("weight", 1)
            new_graph.add_edge(c1, c2, weight=new_weight)
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
            if self.pre_split_communities!=None:
                new_pre_split_communities[relabelled_communities[community]] = \
                    self.pre_split_communities[community]
                
        
        if self.pre_split_communities!=None:
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


def detect_communities(G, verbose=False, randomized=False, splitting_func=None, remerge=False):
    """Returns the detected communities as a list of lists of nodes
    representing each community.
    Uses the Louvain heuristic from:
        Blondel, V.D. et al. Fast unfolding of communities in
    large networks. J. Stat. Mech 10008, 1 - 12(2008).
    """
    louvain = Louvain(G, verbose=verbose, randomized=randomized, splitting_func=splitting_func, remerge=remerge)
    louvain.run()
    return louvain.communities, louvain.community_map

def louvainfunc(G, verbose=False, randomized=False, splitting_func=None, remerge=False):
    louvain = Louvain(G, verbose=verbose, randomized=randomized, splitting_func=None, remerge=remerge)
    louvain.run()
    return louvain.community_map