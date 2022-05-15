import networkx as nx
import scipy
from louvain import detect_communities
import newmanGirvan
import community_newman
import time

G = nx.karate_club_graph()
#G = nx.read_edgelist(r"C:\Users\sabam\OneDrive - mail.tau.ac.il\Biological Networks\Benchmarks\Benchmarks\talya\edges.txt")
start = time.time()
partition = detect_communities(G, splitting_func=newmanGirvan.newmanGirvan)
end = time.time()
print("split: ", end - start)
start = time.time()
partition1 = detect_communities(G)
end = time.time()
print("no split: ", end - start)
