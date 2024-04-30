import networkx as nx
import time
import sys, os
import threading
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
from matplotlib import pyplot as plt

from adhoccomputing.GenericModel import Topology

from TORA.TORAComponent import TORANode, TORAHeight, heights, all_edges, wait_for_action_to_complete

def deterministic_test1():
    graph = nx.Graph()

    graph.add_edge(0, 1)
    graph.add_edge(0, 7)
    graph.add_edge(0, 3)
    graph.add_edge(1, 6)
    graph.add_edge(6, 5)
    graph.add_edge(6, 4)
    graph.add_edge(4, 2)

    # nx.draw(G, with_labels=True, font_weight="bold")
    # plt.draw()
    # plt.show()
    # plt.savefig("InitialGraph.png")

    # print(f"Threads count 1: {threading.active_count()}")

    topology = Topology()
    topology.construct_from_graph(graph, TORANode, GenericChannel)
    
    destination_id = 7
    source_id = 0
    destination_height: TORAHeight = TORAHeight(0, 0, 0, 0, destination_id)
    
    topology.start()
    
    t = time.time()
    topology.nodes[destination_id].app_layer.set_height(destination_height)
    topology.nodes[source_id].app_layer.process_query_message(destination_id, source_id)
    print(wait_for_action_to_complete() - t)


    # DRAW Final DAG 
    dag = nx.DiGraph()
    for node, height in heights(topology):
        dag.add_node(node, label=height)
    edges = all_edges(topology)
    dag.add_edges_from(edges)

    nx.draw(dag, with_labels=True, font_weight="bold", arrows=True)
    plt.draw()
    # plt.show()
    plt.savefig("FinalGraph.png")

def random_test_by_graph_size(size, destination_id=7, source_id=0, save_graph=False):
    graph = nx.random_tree(size)
    # nx.draw(G, with_labels=True, font_weight="bold")
    # plt.draw()
    # plt.show()


    time_list = []
    graph_construction_time = time.time()
    print("Graph size: ", graph.number_of_nodes())
    topology = Topology()
    topology.construct_from_graph(graph, TORANode, GenericChannel)
    print("Constructed topology with time: ", time.time() - graph_construction_time)
    time_list.append(time.time() - graph_construction_time)
    
    destination_height: TORAHeight = TORAHeight(0, 0, 0, 0, destination_id)
    
    topology.start()
    start_time = time.time()
    topology.nodes[destination_id].app_layer.set_height(destination_height)
    topology.nodes[source_id].app_layer.process_query_message(destination_id, source_id)
    print("Waiting for action to complete")
    end_time = wait_for_action_to_complete()
    print(f"Routing done. Time to complete: {end_time - start_time}")
    time_list.append(end_time - start_time)
    

    dag = nx.DiGraph()
    for node, height in heights(topology):
        dag.add_node(node, label=height)
    edges = all_edges(topology)
    dag.add_edges_from(edges)

    if save_graph:
        nx.draw(dag, with_labels=True, font_weight="bold", arrows=True)
        plt.draw()
        # plt.show()
        figures_dir = "/workspace/tests/figures"
        plt.savefig(f"{figures_dir}/FinalGraph.png")

def main():
    # setAHCLogLevel(DEBUG)
    # deterministic_test1()
    # random_test_by_graph_size(size=8, source_id=0, destination_id=7, save_graph=True)
    random_test_by_graph_size(size=200, source_id=0, destination_id=99)
    # random_test_by_graph_size(size=1000, source_id=0, destination_id=999)
    

if __name__ == "__main__":
    main()
