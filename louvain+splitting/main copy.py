import networkx as nx
import scipy
import sys
import louvain
#from louvain import detect_communities
import newmanGirvan
import community_newman
import time
from datetime import datetime
import evaluation


# G = nx.karate_club_graph()
# comms, dic = louvain.detect_communities(G, splitting_func=louvain.louvainfunc, remerge=True)
# exit()              
# # G = nx.read_edgelist(r"C:\Users\sabam\OneDrive - mail.tau.ac.il\Biological Networks\Benchmarks\Benchmarks\LFRBenchmark\Graphs\1000_0.5_0\network.dat", nodetype=int)

# start = time.time()
# partition = detect_communities(G, splitting_func=newmanGirvan.newmanGirvan, remerge=False)
# end = time.time()
# print("girvan split: ", end - start)

# start = time.time()
# partition = detect_communities(G, splitting_func=community_newman.partition, remerge=False)
# end = time.time()
# print("newman split: ", end - start)

# start = time.time()
# partition1 = detect_communities(G)
# end = time.time()
# print("no split: ", end - start)


n_vals=(1000, 10000)
mu_vals=(0.4, 0.5, 0.6) 
num_of_benchmarks=10
now = datetime.now()
dt_string = now.strftime("%d_%m_%Y__%H_%M")
fpath = dt_string+".csv"
f = open(fpath, "w")
f.write("network,method,time,modularity,cunductance,accurary")
f.write("\n");
f.close()


netPath = sys.path[0]+r"\..\Graphs\{0}\network.dat"
commPath =  sys.path[0]+r"\..\Graphs\{0}\community.dat"

def write_result(f, network, method, time_, comms, Y, X):
    modularity = str(evaluation.mod(G, comms))
    cunductance = str(evaluation.cond(G, comms))
    accurary = str(evaluation.jaccard(X, Y))
    f.write(",".join([network,method,time_,modularity,cunductance,accurary]))
    f.write("\n");

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
        d[int(node)]=int(comm)
    return d


for i in range(num_of_benchmarks):
    for mu in mu_vals:
        for n in n_vals:
            network = f"{n}_{mu}_{i}"
            netfile = netPath.format(network)
            real_comms = get_comm_dic(commPath.format(network))
            G = nx.read_edgelist(netfile, nodetype=int)

            f = open(fpath, "a")
            ## NORMAL LOUVAIN
            print(network+"## NORMAL LOUVAIN")
            try:
                start = time.time()
                comms, dic = louvain.detect_communities(G, randomized=True)
                end = time.time()
                time_ = str(end - start)
                write_result(f, network, "normal louvain", time_, comms, dic, real_comms)
            except:
                print("FAILED")
                f.write(network+",normal louvain,FAILED,FAILED,FAILED,FAILED")
                f.write("\n");
            f.close()

            # ## NORMAL NEWMAN
            # print(network+"## NORMAL NEWMAN")
            # try:
            #     start = time.time()
            #     dic = community_newman.partition(G)
            #     comms = get_comms_from_dic(dic)
            #     end = time.time()
            #     time_ = str(end - start)
            #     write_result(f, network, "normal newman", time_, comms, dic, real_comms)
            # except:
            #     print("FAILED")
            #     f.write(network+",normal newman,FAILED,FAILED,FAILED,FAILED")
            #     f.write("\n");
            
            f = open(fpath, "a")
            ## SPLIT LOUVAIN NO REMERERGE
            print(network+"## SPLIT LOUVAIN NO REMERERGE")
            try:
                start = time.time()
                comms, dic = louvain.detect_communities(G, splitting_func=louvain.louvainfunc, remerge=False, randomized=True)
                end = time.time()
                time_ = str(end - start)
                write_result(f, network, "split_louvain", time_, comms, dic, real_comms)
            except:
                print("FAILED")
                f.write(network+",split_louvain,FAILED,FAILED,FAILED,FAILED")
                f.write("\n");
            f.close()

            f = open(fpath, "a")
            ## SPLIT LOUVAIN WITH REMERERGE
            print(network+"## SPLIT LOUVAIN WITH REMERERGE")
            try:
                start = time.time()
                comms, dic = louvain.detect_communities(G, splitting_func=louvain.louvainfunc, remerge=True, randomized=True)
                end = time.time()
                time_ = str(end - start)
                write_result(f, network, "split_louvain_remerge", time_, comms, dic, real_comms)
            except:
                print("FAILED")
                f.write(network+",split_louvain_remerge,FAILED,FAILED,FAILED,FAILED")
                f.write("\n");
            f.close()

            f = open(fpath, "a")
            ## SPLIT GIRVAN NO REMERERGE
            print(network+"## SPLIT GIRVAN NO REMERERGE")
            try:
                start = time.time()
                comms, dic = louvain.detect_communities(G, splitting_func=newmanGirvan.newmanGirvan, remerge=False, randomized=True)
                end = time.time()
                time_ = str(end - start)
                write_result(f, network, "split_girvan", time_, comms, dic, real_comms)
            except:
                print("FAILED")
                f.write(network+",split_girvan,FAILED,FAILED,FAILED,FAILED")
                f.write("\n");
            f.close()

            f = open(fpath, "a")
            ## SPLIT GIRVAN WITH REMERERGE
            print(network+"## SPLIT GIRVAN WITH REMERERGE")
            try:
                start = time.time()
                comms, dic = louvain.detect_communities(G, splitting_func=newmanGirvan.newmanGirvan, remerge=True, randomized=True)
                end = time.time()
                time_ = str(end - start)
                write_result(f, network, "split_girvan_remerge", time_, comms, dic, real_comms)
            except:
                print("FAILED")
                f.write(network+",split_girvan_remerge,FAILED,FAILED,FAILED,FAILED")
                f.write("\n");             
            f.close()

            # f = open(fpath, "a")
            # ## SPLIT NEWMAN NO REMERERGE
            # print(network+"## SPLIT NEWMAN NO REMERERGE")
            # try:
            #     start = time.time()
            #     comms, dic = louvain.detect_communities(G, splitting_func=community_newman.partition, remerge=False, randomized=True)
            #     end = time.time()
            #     time_ = str(end - start)
            #     write_result(f, network, "split_newman", time_, comms, dic, real_comms)
            # except:
            #     print("FAILED")
            #     f.write(network+",split_newman,FAILED,FAILED,FAILED,FAILED")
            #     f.write("\n");
                               
            # f.close() 
            # f = open(fpath, "a")
            # ## SPLIT NEWMAN WITH REMERERGE
            # print(network+"## SPLIT NEWMAN WITH REMERERGE")
            # try:
            #     start = time.time()
            #     comms, dic = louvain.detect_communities(G, splitting_func=community_newman.partition, remerge=True, randomized=True)
            #     end = time.time()
            #     time_ = str(end - start)
            #     write_result(f, network, "split_newman_remerge", time_, comms, dic, real_comms)
            # except:
            #     print("FAILED")
            #     f.write(network+",split_newman_remerge,FAILED,FAILED,FAILED,FAILED")
            #     f.write("\n");
            # f.close() 

            f = open(fpath, "a")
            ## SPLIT NX.GIRVAN_MOD NO REMERERGE
            print(network+"## SPLIT NX.GIRVAN_MOD NO REMERERGE")     
            try:
                start = time.time()
                comms, dic = louvain.detect_communities(G, splitting_func=newmanGirvan.networkxMaxModularity, remerge=False, randomized=True)
                end = time.time()
                time_ = str(end - start)
                write_result(f, network, "split_nx.girvan_mod", time_, comms, dic, real_comms)
            except:
                print("FAILED")
                f.write(network+",split_nx.girvan_mod,FAILED,FAILED,FAILED,FAILED")
                f.write("\n");
            f.close() 

            ## SPLIT NX.GIRVAN_MOD WITH REMERERGE
            f = open(fpath, "a")
            print(network+"## SPLIT NX.GIRVAN_MOD WITH REMERERGE")
            try:
                start = time.time()
                comms, dic = louvain.detect_communities(G, splitting_func=newmanGirvan.networkxMaxModularity, remerge=True, randomized=True)
                end = time.time()
                time_ = str(end - start)
                write_result(f, network, "split_nx.girvan_mod_remerge", time_, comms, dic, real_comms)
            except:
                print("FAILED")
                f.write(network+",split_nx.girvan_mod_remerge,FAILED,FAILED,FAILED,FAILED")
                f.write("\n");
            f.close()

            ## SPLIT NX.GIRVAN_CON NO REMERERGE
            f = open(fpath, "a")
            print(network+"## SPLIT NX.GIRVAN_CON NO REMERERGE")
            try:
                start = time.time()
                comms, dic = louvain.detect_communities(G, splitting_func=newmanGirvan.networkxMaxConductance, remerge=False, randomized=True)
                end = time.time()
                time_ = str(end - start)
                write_result(f, network, "split_nx.girvan_con", time_, comms, dic, real_comms)
            except:
                print("FAILED")
                f.write(network+",split_nx.girvan_con,FAILED,FAILED,FAILED,FAILED")
                f.write("\n");
            f.close()
            
            ## SPLIT NX.GIRVAN_CON WITH REMERERGE
            print(network+"## SPLIT NX.GIRVAN_CON WITH REMERERGE")
            f = open(fpath, "a")
            try:
                start = time.time()
                comms, dic = louvain.detect_communities(G, splitting_func=newmanGirvan.networkxMaxConductance, remerge=True)
                end = time.time()
                time_ = str(end - start)
                write_result(f, network, "split_nx.girvan_con_remerge", time_, comms, dic, real_comms)
            except:
                print("FAILED")
                f.write(network+",split_nx.girvan_con_remerge,FAILED,FAILED,FAILED,FAILED")
                f.write("\n");
            f.close()

            f = open(fpath, "a")
            f.write("\n");
            f.close()

f.close()       