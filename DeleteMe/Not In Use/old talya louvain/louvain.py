import random

NODE == 0
WEIGHT == 1

class Node():
    def __init__(self, name):
        self.neighbors = {}
        self.community = None
        self.ki = 0
        self.name = name

    def add_neighbor(n, w=1):
        if not n.name in neighbors:
            neighbors[n.name]=[n,0]
        neighbors[n.name][WEIGHT] += w
        ki += w

    def get_name():
        return name

    def get_comm():
        return community

    def set_comm(c):
        community = c

    def add_to_comm(c):
        if community != None:
            community.remove_member(self)
        community = c
        c.add_member(self)
         
    def make_comm():
        c = Community(name)
        self.add_to_comm(c)

    def modularity_gain(c,m):
        k_in = sum([neighbors[n][WEIGHT] for n in neighbors if neighbors[n][NODE].community == c])
        # dQ = (c.sum_in + 2*k_in)/(2*m) - ((c.sum_tot + ki)/(2*m))**2 \
        #     - (c.sum_in/2*m - (c.sum_tot/2*m)**2 - (ki/2*m)**2)
        dQ = (2*m*(c.sum_in + 2*k_in) - (c.sum_tot + ki)**2 \
            - (2*m*c.sum_in - c.sum_tot**2 - ki**2))/((2*m)**2)
        return dQ
    
class Community():
    def __init__(self):
        self.members = set()
        self.sum_in = 0 # sum of all edges inside comminty
        self.sum_tot = 0 # sum of all edges that at least on side of them is in the community
        self.size = 0 # num of nodes inside
        self.name = name # unique name (string)
    
    def get_name():
        return name

    def add_node(node):
        members.add(node)
        size = len(members)
        sum_tot += node.ki
        neighbors = node.neighbors
        c = self
        sum_in += sum([neighbors[n][WEIGHT] for n in neighbors if neighbors[n][NODE].community == c])
    
    def remove_node(node):
        members.remove(node)
        size = len(members)
        sum_tot -= node.ki
        sum_in -= sum([neighbors[n][WEIGHT] for n in neighbors if neighbors[n][NODE].community == c])

def create_node_dictionary_from_file(file_name):
    node_d = {}
    edge_count = 0
    with open(file_name) as f:
        for line in f.readlines():
            edge_count += 1
            a, b = line.split()
            if not a in node_d:
                node_d[a] = new_node(a)
            if not b in node_d:
                node_d[b] = new_node(b)
            node_d[a].add_neighbor(vd[b])
            node_d[b].add_neighbor(vd[a])

    for i in node_d:
        node_d[i].make_comm()

    return node_d, edge_count

def graph_modularity(node_dic, m):
    Q = 0
    for i in node_dic:
        node = node_dic[i]
        for neighbor in node.neighbors:
            if node.get_comm() == neighbor.get_comm():
                Q += 1 - node.degree*neighbor.degree/(2*m)
    return Q/(2*m)

def move_nodes(node_dic, m):

    dQ_tot = 0

    for i in node_dic:
        node = node_dic[i]
        dQ_max = 0
        comm_max = node.get_comm()
        for v in node.neighbors:
            if v.get_comm() != node.get_comm():
                dQ = node.modularity_gain(v.get_comm(),m)
                if dQ>dQ_max:
                    dQ_max = dQ
                    comm_max = v.get_comm()
        if comm_max != node.get_comm():
            node.add_to_comm(comm_max)
            dQ_tot += dQ

    return dQ_tot
    
def group_communities(node_dic):
    new_dic = {}
    id = 0

    for i in node_dic: # find all communities that have some node assigned to them
        c = node_dic[i].get_comm()
        c_name = c.get_name()
        if not c_name in new_dic: # make a new node from this community
            new_dic[c_name] = new_node(c_name)
        node =  new_dic[c_name]

        # each community will have a self loop of size sum_in (sum of all edges inside comminty)
        node.add_neighbor(node, c.sum_in)

        # if this node has neighbors, their communities will also be neighbors
        for j in node_dic[i].neighbors:
            nc_name = neighbors[j][NODE].get_comm().get_name()
            if nc_name == c_name: # edges between node of the same comminty are already counted in sum_in, so i'll skip them
                continue

            if not nc_name in new_dic:
                new_dic[nc_name] = new_node(nc_name)

            node.add_neighbor(new_dic[nc_name])

    return new_dic

def update_clustering(node_dic, new_nodes):

    for i in node_dic:
        old = node_dic[i].get_comm().get_name()
        new = new_nodes[old].get_comm()
        node_dic[i].set_comm(new)

def louvain(node_dic, m):
    # gets a dic of individual nodes
    # returns 1 if it was able to improve the clustering, 0 else

    if len(node_dic==1):
        return 0 # no change was done

    # move nodes between communities 
    dQ = move_nodes(node_dic, m)
    if dQ == 0:
        return 0 # no change was done

    while dQ > 0:
        dQ = move_nodes(node_dic, m)

    # split communities
    # after split, regroup
    new_nodes = group_communities(node_dic) # should be fixed, so comms that are splitted will be in same community
    # or instead of fixing it, regroup and then edit so comms that are splitted will be in same community

    rec_val = louvain(new_nodes, m) # recursivly recluster super-communities
    if rec_val: # if super-nodes managed to recluster
        update_clustering(node_dic, new_nodes)
    # even if super-nodes didn't recluster, regular nodes did
    return 1 

def main():
    node_dic, m = create_node_dictionary_from_file(file_name)
    louvain(node_dic, m)
    Q = graph_modularity(node_dic, m)
    # evaluate correctness















def create_vertex_array_from_LFRB_file(file_name, n):
    v_arr = [None for i in range(n)]
    with open(file_name) as f:
        for line in f.readlines():
            i, j = [int(i)-1 for k in line.split()]
            for v in (i,j):
                if v_arr[v] == None:
                    node = Node()
                    c = Community([node])
                    node.community = c
                    v_arr[v] = node
            v_arr[i].neighbors.append(v_arr[j])
            v_arr[j].neighbors.append(v_arr[i])
