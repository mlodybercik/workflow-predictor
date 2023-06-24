#!/bin/bash
nodes=("reload-b3-audit" "reload-b3-tables" "b3-calc-completed" "run-b3-calculation" "complete-strategic-harmonization-job" "run-data-harmonization" "run-data-staging" "land-f1mdl-data" "start-strategic-batch" "init-strategic-batch" "open-date-card" "f1-notification-trigger")
for node in ${nodes[@]}; do
    echo "doing $node"
    TF_CPP_MIN_LOG_LEVEL=3 python src/app.py -d $1 -b 8 -e 8 -j $node learn
done
