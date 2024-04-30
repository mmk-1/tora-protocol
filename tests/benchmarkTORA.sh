#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <n>"
    exit 1
fi

n=$1

for (( i=5; i<=n; i++ ))
do
    if (( i % 5 == 0 )); then
        echo "Running test with $i nodes"
        python3 topologyTORATest.py $i
    fi
done