import pickle
import matplotlib.pyplot as plt
import numpy as np
import os

figures_dir = "/workspace/tests/topology_benchmark_figures"
test_dir = "/workspace/tests"

def main():
    if os.path.exists(f"{test_dir}/benchmark_times.pkl"):
        with open(f"{test_dir}/benchmark_times.pkl", "rb") as f:
            benchmark_times = pickle.load(f)
    print(len(benchmark_times))
    topology_sizes = list(range(5, (len(benchmark_times) * 5) + 5, 5))
    print(topology_sizes)
    plt.figure(figsize=(10, 6))
    plt.plot(topology_sizes, benchmark_times, marker='o')
    plt.title('Benchmark Times vs Topology Sizes')
    plt.xlabel('Topology Size (Number of Nodes)')
    plt.ylabel('Time Taken (s)')
    plt.grid(True)

    # Set x-axis ticks at intervals of 10
    plt.xticks(np.arange(min(topology_sizes), max(topology_sizes)+1, 10), 
            [str(int(i)) for i in np.arange(min(topology_sizes), max(topology_sizes)+1, 10)])

    plt.savefig(f"{figures_dir}/benchmark_chart.png")
    plt.close()

if __name__ == "__main__":
    main()