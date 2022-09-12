from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import networkx as nx
import scipy
import sys
import os
import traceback
import time
from datetime import datetime
import yemenitestep.evaluation as evaluation
from threading import Thread
import yemenitestep.yemenitestep as ys

n_vals = [1000, 10000]
mu_vals = (0.4, 0.5, 0.6)
num_of_benchmarks = 10
now = datetime.now()
dt_string = now.strftime("%d_%m_%Y__%H_%M")
methods_to_test = [
    "None",
    "Louvain",
    "GN_modularity",
    "GN_conductance",
    #"Newman",
]
randomized = [True, False]
remerge = [True, False]
relative = [False]

def write_result(f, num, size, mu, method, rnd, rmrg, rltv, time_, comms, Y, X, G) :
    modularity = str(evaluation.modularity(G, comms))
    cunductance = str(evaluation.conductance(G, comms))
    accurary = str(evaluation.jaccard(X, Y))
    f.write(f"{num},{size},{mu},{method},{rnd},{rmrg},{rltv},{time_},{modularity},{cunductance},{accurary}")
    f.write("\n")


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

def make_comm_dic(comms):
    community_map = {}
    for comm in comms:
        for node in comm:
            community_map[node] = comm
    return community_map

def run_test(fpath, method, rnd, rmrg, rltv):
    
    for mu in mu_vals:
        for n in n_vals: 
            for i in range(num_of_benchmarks):

                network = f"{n}_{mu}_{i}"
                netPath = sys.path[0]+r"/../Graphs/{0}/network.dat"
                commPath = sys.path[0]+r"/../Graphs/{0}/community.dat"
            
                netfile = netPath.format(network)
                real_comms = get_comm_dic(commPath.format(network))
                G = nx.read_edgelist(netfile, nodetype=int)

                f = open(fpath, "a")
                method = None if method=="None" else method
                try:
                    start = time.time()
                    comms = ys.get_communities(G, splitting_func=method, randomized=rnd, remerge=rmrg ,relative=rltv)
                    end = time.time()
                    time_ = str(end - start)
                    method = method if method else "None"
                    dic = make_comm_dic(comms)
                    write_result(f, i, n, mu, method, rnd, rmrg, rltv, time_, comms, dic, real_comms, G)
                    print(f"Finished running {method}, on network {network}")

                except BaseException as ex:
                    
                    # Get current system exception
                    ex_type, ex_value, ex_traceback = sys.exc_info()

                    # Extract unformatter stack traces as tuples
                    trace_back = traceback.extract_tb(ex_traceback)

                    # Format stacktrace
                    stack_trace = list()

                    for trace in trace_back:
                        stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

                    print(method+"on"+network+" FAILED")
                    f.write(network+","+"ERROR")
                    f.write("Exception type : %s " % ex_type.__name__)
                    f.write("Exception message : %s" %ex_value)
                    f.write("Stack trace : %s" %stack_trace)
                    f.write("\n");

                f.close()




def main():
    executor = ProcessPoolExecutor(max_workers=10)
    threads = []
    counter = 0
    
    os.mkdir(sys.path[0]+'/../Results/'+dt_string)

    for method in methods_to_test:
        os.mkdir(sys.path[0]+'/../Results/'+dt_string+"/"+method)
        for rnd in randomized:
            for rmrg in remerge:
                if rmrg and method=="None": continue
                for rltv in relative:
                    if rltv:
                        if method not in ["Louvain","GN_modularity"]: continue
                    # create result file
                    fpath = sys.path[0]+f'/../Results/{dt_string}/{method}/rnd-{rnd}_rmrg-{rmrg}_rltv-{rltv}.csv'
                    f = open(fpath, "w")
                    f.write("i,size,mu,method,random,remerge,relative,time,modularity,conductance,jaccard")
                    f.write("\n")
                    f.close()

                    #run_test(n, fpath, method)
                    task = executor.submit(run_test, fpath, method, rnd, rmrg, rltv)
                    print("starting thread: "+str(counter))
                    counter += 1
                    # #run_test(n, mu, i, fpath)

    print(task.result())    

if __name__ == '__main__':
    main()
