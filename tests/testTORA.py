import networkx as nx
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
from matplotlib import pyplot as plt

from adhoccomputing.GenericModel import Topology

from TORA.TORAComponent import RoutingTORAComponent, TORAHeight, heights, all_edges, wait_for_action_to_complete


def main():
    # G = nx.random_tree(8)
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
    # exit(69)


    topo = Topology()
    topo.construct_from_graph(G, RoutingTORAComponent, GenericChannel)
    print(f"len: {len(topo.nodes)}")
    destination_id = 7
    source_id = 0
    destination_height: TORAHeight = TORAHeight(0, 0, 0, 0, destination_id)
    topo.start()

    t = time.time()
    topo.nodes[destination_id].set_height(destination_height)
    topo.nodes[source_id].init_route_creation(destination_id)
    print(wait_for_action_to_complete() - t)
    # topo.nodes[source_id].send_message(destination_id, "Hey there! Test message")


    # DRAW Final DAG 
    G2 = nx.DiGraph()
    print(len(heights(topo)))
    print(heights(topo))
    for node, height in heights(topo):
        G2.add_node(node, label=height)
    edges = all_edges(topo)
    G2.add_edges_from(edges)
    print(f"edges: {edges}")

    nx.draw(G2, with_labels=True, font_weight="bold", arrows=True)
    plt.draw()
    plt.show()

if __name__ == "__main__":
    main()
