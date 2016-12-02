#!/bin/bash

echo $1
for i in {1..5}
do
    echo $i
    python simulation.py -l $1 -b 10 -g 3
    python simulation.py -l $1 -b 10 -s opt
    python simulation.py -l $1 -b 10 -s approx
    python simulation.py -l $1 -b 10 -s greedy
    python simulation.py -l $1 -b 10 -s perf
    python simulation.py -l $1 -b 10 -s operation
    python simulation.py -l $1 -b 10 -s static
done
