import pickle
import networkx as nx
import time
import sys, os
import threading
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
from matplotlib import pyplot as plt

from adhoccomputing.GenericModel import Topology
import numpy as np

from TORA.TORAComponent import TORANode, TORAHeight, heights, all_edges, set_benchmark_time, wait_for_action_to_complete

figures_dir = "/workspace/tests/topology_benchmark_figures"

topology_size = int(sys.argv[1])

def run_tora_test(size, destination_id=7, source_id=0, save_graph=False):
    global figures_dir
    graph = nx.random_tree(size)
    if save_graph:
        nx.draw(graph, with_labels=True, font_weight="bold")
        plt.draw()
        plt.savefig(f"{figures_dir}/size_{size}/InitialGraph.png")
        plt.close()

    time_list = []
    graph_construction_time = time.time()
    print("Graph size: ", graph.number_of_nodes())
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
        plt.savefig(f"{figures_dir}/size_{size}/FinalGraph.png")
        plt.close()
    
    return sum(time_list)

def main():
    # setAHCLogLevel(DEBUG)
    benchmark_times = []
    
    # Load the benchmark times if they exist
    if os.path.exists("benchmark_times.pkl"):
        with open("benchmark_times.pkl", "rb") as f:
            benchmark_times = pickle.load(f)
            len(benchmark_times)

    if not os.path.exists(f"{figures_dir}/size_{topology_size}"):
        os.makedirs(f"{figures_dir}/size_{topology_size}")
    
    temp_time = []
    for j in range(3):
        set_benchmark_time()
        temp_time.append(run_tora_test(size=topology_size, source_id=0, destination_id=topology_size-1, save_graph=True))
    
    benchmark_times.append(sum(temp_time) / 3)
    with open("benchmark_times.pkl", "wb") as f:
        pickle.dump(benchmark_times, f)

    # plt.figure(figsize=(10, 6))
    # plt.plot(topology_sizes, benchmark_times, marker='o')
    # plt.title('Benchmark Times vs Topology Sizes')
    # plt.xlabel('Topology Size (Number of Nodes)')
    # plt.ylabel('Time Taken (s)')
    # plt.grid(True)

    # # Set x-axis ticks at intervals of 10
    # plt.xticks(np.arange(min(topology_sizes), max(topology_sizes)+1, 10), 
    #         [str(int(i)) for i in np.arange(min(topology_sizes), max(topology_sizes)+1, 10)])

    # plt.savefig(f"{figures_dir}/benchmark_chart.png")
    # plt.close() 

if __name__ == "__main__":
    main()
