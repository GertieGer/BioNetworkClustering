import networkx as nx
  
  
def edge_to_remove(g):
      
    d1 = nx.edge_betweenness_centrality(g)
    list_of_tuples = list(d1.items())
      
    sorted(list_of_tuples, key = lambda x:x[1], reverse = True)
      
    # Will return in the form (a,b)
    return list_of_tuples[0][0]
  
def girvan(g):
    a = nx.connected_components(g)
    lena = len(list(a))
    print (' The number of connected components are ', lena)
    while (lena == 1):
  
        # We need (a,b) instead of ((a,b))
        u, v = edge_to_remove(g)
        g.remove_edge(u, v) 
          
        a = nx.connected_components(g)
        lena=len(list(a))
        print (' The number of connected components are ', lena)
    
    return a
  
# Driver Code
g = nx.barbell_graph(5,0)
a = girvan(g)
print ('Barbell Graph')
  
for i in a:
    print (i.nodes())
    print ('.............')
  
g1 = nx.karate_club_graph()
a1 = girvan(g1)
  
print ('Karate Club Graph')
for i in a1:
    print (i.nodes())
    print ('.............')