from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import networkx as nx
import networkx.algorithms.community as nx_comm
import scipy
import sys
import os
import traceback
import time
from datetime import datetime
import evaluation
from threading import Thread
import yemenitestep as ys


now = datetime.now()
dt_string = now.strftime("%d_%m_%Y__%H_%M")

netwroks_to_test = [
    # {
    #     'name': '100_0.4_0',
    #     'network': sys.path[0]+r"/../Graphs/100_0.4_0/network.dat",
    #     'clusters': sys.path[0]+r"/../Graphs/100_0.4_0/community.dat"
    # },
    # {
    #     'name': 'Yeast',
    #     'network': sys.path[0]+r"/../Graphs/Yeast/edges.txt",
    #     'clusters': sys.path[0]+r"/../Graphs/Yeast/clusters.txt"
    # },
    # {
    #     'name': 'Arabidopsis',
    #     'network': sys.path[0]+r"/../Graphs/Arabidopsis/edges.txt",
    #     'clusters': sys.path[0]+r"/../Graphs/Arabidopsis/clusters.txt"
    # },
    {
        'name': 'ca-CondMat',
        'network': sys.path[0]+r"/../Graphs/ca-CondMat.txt",
        'clusters': None
    },
]


def write_result(f, name, method, time_, comms, Y, X, G) :
    print("writing results")
    modularity = str(evaluation.modularity(G, comms))
    cunductance = str(evaluation.conductance(G, comms))
    accuracy = str(evaluation.accuracy(X, Y)) if X else "NA"
    f.write(f"{name},{method},{time_},{modularity},{cunductance},{accuracy}")
    f.write("\n")


def get_comms_from_dic(community_map):
    inverted_community_map = defaultdict(list)
    for node in community_map:
        inverted_community_map[community_map[node]].append(node)
    return list(inverted_community_map.values())


def get_comm_dic(path):
    if path is None: return None
    d = {}
    f = open(path, "r")
    lines = f.readlines()
    for line in lines:
        try:
            node, comm = line.strip().split('\t')
        except:
            pass
        d[node] = comm
    return d

def make_comm_dic(comms):
    community_map = {}
    for comm in comms:
        for node in comm:
            community_map[node] = comm
    return community_map

def run_test(network, method, G, real_comms):
    
    out_file = sys.path[0]+f"/../Results/{dt_string}_{network['name']}_{method}.csv"
    print(f"Started {method} on {network['name']} ({datetime.now().strftime('%d_%m_%Y__%H_%M')})")

    try:
        start = time.time()
        if method == 'YSGN_mod':
            comms = ys.get_communities(G, "GN_modularity", randomized=True, remerge=False ,relative=True, verbose=True)
        if method == 'YSLouvain':
            comms = ys.get_communities(G, "Louvain", randomized=False, remerge=False ,relative=False, verbose=True)
        if method == 'Louvain':
            comms = nx_comm.louvain_communities(G)
        if method == 'Newman':
            return

        end = time.time()
        time_ = str(end - start)
        dic = make_comm_dic(comms)
        f = open(out_file, "w")
        write_result(f, network['name'], method, time_, comms, dic, real_comms, G)

    except BaseException as ex:
        
        ex_type, ex_value, ex_traceback = sys.exc_info()
        trace_back = traceback.extract_tb(ex_traceback)
        stack_trace = list()
        for trace in trace_back:
            stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

        print(method+"on"+network+" FAILED")
        f.write(network+","+"ERROR")
        f.write("Exception type : %s " % ex_type.__name__)
        f.write("Exception message : %s" %ex_value)
        f.write("Stack trace : %s" %stack_trace)
        f.write("\n");

    mins = (end - start)/60
    print(f"Finished {method} on {network['name']} in {mins} minutes")
    f.close()



def main():
    # executor = ProcessPoolExecutor(max_workers=10)
    # threads = []
    # counter = 0
    
    for network in netwroks_to_test:
        real_comms = get_comm_dic(network['clusters'])
        G = nx.read_edgelist(network['network'], delimiter='\t')
        for method in ['YSGN_mod']:
            run_test(network, method, G, real_comms)
            #task = executor.submit(run_test, network, method, G, real_comms) # does not block
            # print("starting thread: "+str(counter))
            # counter += 1
            # #run_test(n, mu, i, fpath)

    #print(task.result())    

if __name__ == '__main__':
    main()
