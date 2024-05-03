#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <n>"
    exit 1
fi

n=$1

# # Start from at least 5 nodes and only count by 5
# for (( i=5; i<=n; i++ ))
# do
#     if (( i % 5 == 0 )); then
#         echo "Running test with $i nodes"
#         python3 topologyTORATest.py $i
#     fi
# done

graph_types=(
    "complete_graph" 
    # "random_tree" 
    # "star_graph" 
    # "cycle_graph"
)

# Start from at least 5 nodes and only count by 5
for graph_type in ${graph_types[@]}
do
    for (( i=5; i<=n; i++ ))
    do
        if (( i % 5 == 0 )); then
            # for (( j=0; j<=3; j++ ))
            # do
                # echo "Running test with $i nodes for $graph_type"
            python3 topologyTORATest.py $i $graph_type
            # done
        fi
    done
done