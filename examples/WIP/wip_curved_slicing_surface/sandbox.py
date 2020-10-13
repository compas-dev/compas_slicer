import networkx as nx

G = nx.Graph()

G.add_edge(5,6)
G.add_edge(6,9)
G.add_edge(5,9)

print(G.adjacency())

for k in G.adjacency():
    print (k)
# print (len(list(nx.neighbors(G, 5))))

