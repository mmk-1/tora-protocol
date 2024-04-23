import networkx as nx
from matplotlib import pyplot as plt


def main():
    G = nx.Graph()

    G.add_edge(0, 1)
    G.add_edge(0, 7)
    G.add_edge(0, 3)
    G.add_edge(1, 6)
    G.add_edge(6, 5)
    G.add_edge(6, 4)
    G.add_edge(4, 2)

    nx.draw(G, with_labels=True, font_weight="bold")
    plt.draw()
    plt.show()

if __name__ == "__main__":
    main()