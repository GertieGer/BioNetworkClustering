class CommunityTracker:
    """Class to keep track of network statistics of the network as the
    algorithm progresses and nodes move communities.
    """

    def __init__(self):
        self.node_to_community_map = None
        self.m = 0.0
        self.degrees = None
        self.self_loops = None
        self.community_degrees = None
        self.community_self_loops = None
        self.home_community_map = None

    def initialize_network_statistics(self, G, relative_m=None, relative_k=None):
        self.node_to_community_map = {}
        self.home_community_map = {}
        self.m = G.size(weight="weight") if (relative_m is None) else relative_m
        self.degrees = {}
        self.self_loops = {}
        # Sum of the weights of the edges incident to nodes in C.
        self.community_degrees = {}
        # Sum of the weights of the internal edges in C.
        self.community_self_loops = {}
        # Initialize all nodes in separate communities.
        for community, node in enumerate(G):
            self.node_to_community_map[node] = community
            self.home_community_map[node] = community
            degree = G.degree(node, weight="weight") if (relative_k is None) else relative_k[node]
            self.degrees[node] = self.community_degrees[community] = degree
            self_loop = 0
            if G.has_edge(node, node):
                self_loop = G[node][node].get("weight", 1)
            self.community_self_loops[community] = self.self_loops[node] = self_loop

    def remove(self, node, community, incident_weight):
        """Removes node from community and updates statistics given the
        incident weight of edges from node to other nodes in community.
        """
        self.community_degrees[community] -= self.degrees[node]
        self.community_self_loops[community] -= incident_weight + self.self_loops[node]
        self.node_to_community_map[node] = None

    def insert(self, node, community, incident_weight):
        """Inserts isolated node into community and updates statistics given
        the incident weight of edges from node to other nodes in community.
        """
        self.community_degrees[community] += self.degrees[node]
        self.community_self_loops[community] += incident_weight + self.self_loops[node]
        self.node_to_community_map[node] = community
