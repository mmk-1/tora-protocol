import os
import pickle
import matplotlib.pyplot as plt
import numpy as np

def main():
    proj_dir = os.getcwd()
    
    graph_types = [
        "complete_graph", 
        "random_tree",
        "star_graph",
        "cycle_graph",
        "wheel_graph",
        "ladder_graph",
    ]

    plt.figure(figsize=(10, 6))

    for graph_type in graph_types:
        results_dir = f"{proj_dir}/tests/benchmark_results/{graph_type}"
        bench_dict_dir = f"{results_dir}/benchmark_dict.pkl"

        if os.path.exists(bench_dict_dir):
            with open(bench_dict_dir, "rb") as f:
                benchmark_dict = pickle.load(f)

            # topology_sizes = list(range(5, (len(benchmark_times) * 5) + 5, 5))
            topology_sizes = benchmark_dict.keys()
            benchmark_times = []
            for k in benchmark_dict.keys():
                benchmark_times.append(benchmark_dict[k]['average'])
            plt.plot(topology_sizes, benchmark_times, marker='o', label=graph_type)

    plt.title('Benchmark Times vs Topology Sizes')
    plt.xlabel('Topology Size (Number of Nodes)')
    plt.ylabel('Time Taken (s)')
    plt.grid(True)
    plt.legend()

    # Set x-axis ticks at intervals of 10
    plt.xticks(np.arange(min(topology_sizes), max(topology_sizes)+1, 10), 
            [str(int(i)) for i in np.arange(min(topology_sizes), max(topology_sizes)+1, 10)])

    figures_dir = f"{proj_dir}"
    if not os.path.exists(figures_dir):
        os.makedirs(figures_dir)

    plt.savefig(f"{figures_dir}/benchmark_chart.png")
    plt.close()

if __name__ == "__main__":
    main()
