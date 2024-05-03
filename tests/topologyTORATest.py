import pickle
import networkx as nx
import time
import sys, os
import random
import threading
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
from matplotlib import pyplot as plt

from adhoccomputing.GenericModel import Topology
import numpy as np

from TORA.TORAComponent import TORANode, TORAHeight, heights, all_edges, set_benchmark_time, wait_for_action_to_complete

topology_size = int(sys.argv[1])
graph_type = sys.argv[2]
run_no = int(sys.argv[3])

proj_dir = os.getcwd()
# figures_dir = "/workspace/tests/topology_benchmark_figures"
results_dir = f"{proj_dir}/tests/benchmark_results/{graph_type}"

def generate_source_destination(max_value):
    source = random.randint(0, max_value - 1)
    destination = source
    while destination == source:
        destination = random.randint(0, max_value - 1)
    return source, destination


def nx_graph(graph_type, size):
    if graph_type == 'random_tree':
        graph = nx.random_tree(size)
    elif graph_type == 'complete_graph':
        graph = nx.complete_graph(size)
    elif graph_type == 'cycle_graph':
        graph = nx.cycle_graph(size)
    elif graph_type == 'star_graph':
        graph = nx.star_graph(size)
    return graph

def run_tora_test(graph_type, size, destination_id=7, source_id=0, save_graph=False):
    global results_dir

    # graph = nx.random_tree(size)
    graph = nx_graph(graph_type, size)
    if save_graph:
        nx.draw(graph, with_labels=True, font_weight="bold")
        plt.draw()
        plt.savefig(f"{results_dir}/size_{size}/InitialGraph.png")
        plt.close()

    time_list = []
    graph_construction_time = time.time()
    # print("Graph size: ", graph.number_of_nodes())
    topology = Topology()
    topology.construct_from_graph(graph, TORANode, GenericChannel)
    print("Constructed topology graph with time: ", time.time() - graph_construction_time)
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
        plt.savefig(f"{results_dir}/size_{size}/FinalGraph.png")
        plt.close()

    return sum(time_list)

def main():
    # setAHCLogLevel(DEBUG)
    # benchmark_times = []
    benchmark_dict = {}
    '''
    dict = {
        topo_size = {
            'times': []
            'average': float
        }
    }
    '''
    
    # Load the benchmark times if they exist
    if os.path.exists(f"{results_dir}/benchmark_dict.pkl"):
        with open(f"{results_dir}/benchmark_dict.pkl", "rb") as f:
            benchmark_dict = pickle.load(f)

    if not os.path.exists(f"{results_dir}/size_{topology_size}"):
        os.makedirs(f"{results_dir}/size_{topology_size}")
    
    # sauce, dest = generate_source_destination(topology_size)
    if topology_size not in benchmark_dict:
        benchmark_dict[topology_size] = {}
        benchmark_dict[topology_size]['times'] = []

    # print("Active threads", threading.active_count())
    sauce, dest = generate_source_destination(topology_size)
    print(f"====== GRAPH TYPE: {graph_type}, SIZE: {topology_size} ======")
    print(f"{run_no}: ====== SOURCE: {sauce}, DEST: {dest} ======")
    set_benchmark_time()
    temp_time = run_tora_test(graph_type, size=topology_size, source_id=sauce, destination_id=dest, save_graph=True)

    benchmark_dict[topology_size]['times'].append(temp_time)
    
    n = len(benchmark_dict[topology_size]['times'])
    if n == 3:
        total = sum(benchmark_dict[topology_size]['times'])
        benchmark_dict[topology_size]['average'] = total / n
        print("average: ", benchmark_dict[topology_size]['average'])
    
    # benchmark_times.append(sum(temp_time) / 3)
    with open(f"{results_dir}/benchmark_dict.pkl", "wb") as f:
        pickle.dump(benchmark_dict, f)


if __name__ == "__main__":
    main()
