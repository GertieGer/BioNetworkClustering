import random

class Node():
    def __init__(self):
        self.neighbors = []
        self.community = None
        self.degree = 0

    def add_neighbor(n):
        neighbors.append(n)
        d = len(neighbors)

    def get_comm():
        return community

    def set_comm(c):
        if community != None:
            community.remove_member(self)
        c.add_member(self)
        community = c
        
    def make_comm():
        c = Community()
        self.set_comm(c)

    def modularity_gain(c,m):
        k_in = sum([1 for v in neighbors if v.community == c])
        ki = degree
        # dQ = (c.sum_in + 2*k_in)/(2*m) - ((c.sum_tot + ki)/(2*m))**2 \
        #     - (c.sum_in/2*m - (c.sum_tot/2*m)**2 - (ki/2*m)**2)
        dQ = (2*m*(c.sum_in + 2*k_in) - (c.sum_tot + ki)**2 \
            - (2*m*c.sum_in - c.sum_tot**2 - ki**2))/((2*m)**2)
        return dQ
    
class Community():
    def __init__(self):
        self.members = set()
        self.sum_in = 0
        self.sum_tot = 0
        self.size = 0
    
    def add_node(node):
        members.add(node)
        size = len(members)
        sum_tot += node.degree
        sum_in += sum([1 for v in node.neighbors if v.community == c])
    
    def remove_node(node):
        members.remove(node)
        size = len(members)
        sum_tot -= node.degree
        sum_in -= sum([1 for v in node.neighbors if v.community == c])

def create_node_dictionary_from_file(file_name):
    node_d = {}
    edge_count = 0
    with open(file_name) as f:
        for line in f.readlines():
            edge_count += 1
            a, b = line.split()
            if not a in node_d:
                node_d[a] = new_node()
            if not b in node_d:
                node_d[b] = new_node()
            node_d[a].add_neighbor(vd[b])
            node_d[a].add_neighbor(vd[b])

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

def move_nodes(node_dic, node_order, m):

    dQ_tot = 0

    for i in node_order:
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
            node.set_comm(comm_max)
            dQ_tot += dQ

    return dQ_tot
    
def group_communities(node_dic):
    new_dic = {}
    


def louvain():
    node_order = node_dic.keys()
    random.shuffle(node_order)






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
