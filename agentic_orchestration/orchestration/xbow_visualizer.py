import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
import json

def visualize_xbow_3d(graph_path):
    with open(graph_path) as f:
        data = json.load(f)
    G = nx.json_graph.node_link_graph(data)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    pos = {node: (random.random(), random.random(), random.random()) for node in G.nodes()}
    for node, (x, y, z) in pos.items():
        ax.scatter(x, y, z, label=node, s=20)
        ax.text(x, y, z, node[:12], fontsize=6)

    for u, v in G.edges():
        x = [pos[u][0], pos[v][0]]
        y = [pos[u][1], pos[v][1]]
        z = [pos[u][2], pos[v][2]]
        ax.plot(x, y, z, color='cyan', linewidth=0.5)

    plt.title("XBOW Hidden API Communication Map")
    plt.show()