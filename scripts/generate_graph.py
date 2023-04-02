import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')


jobs = {"complete-b3-strategic-batch":(0,0),
        "complete-strategic-batch":(0,2),
        "skip-regional-batches":(2,0),
        "init-securitization-batch":(4,0),
        "start-securitization-batch":(6,0),
        "run-sec-tactical-staging":(8,0),
        "run-sec-harmonization":(8,2),
        "reload-harmonization-securitization-tables":(10,0),
        "run-b3-securitization":(10,4),
        "mdl-out-b3-with-securitization":(12,2),
        "reload-securitization-tables-b3":(12,0),
        "complete-strategic-batch-sec":(4,2),
        "run-ler-securitization":(14,0),
        "run-b3std-securitization":(14,2),
        "run-lech-securitization":(14,4),
        "run-lvr-securitization":(14,6),
        "reload-securitization-tables-ler":(16,0),
        "reload-securitization-tables-b3std":(16,2),
        "reload-securitization-tables-lech":(16,4),
        "reload-securitization-tables-lvr":(16,6),
        "complete-b3-securitization-batch":(14,8),
        "mdl-out-ler-with-securitization":(18,-2),
        "mdl-out-b3std-with-securitization":(18,0),
        "mdl-out-lech-with-securitization":(18,2),
        "mdl-out-lvr-with-securitization":(18,4),
        "complete-securitization-batch":(20,0),
        "reload-tactical-tables-post-securitization":(22,6),
        "securitization-error-handler":(2,6)}

Labels = {"complete-b3-strategic-batch":1,
        "complete-strategic-batch":2,
        "skip-regional-batches":3,
        "init-securitization-batch":4,
        "start-securitization-batch":5,
        "run-sec-tactical-staging":6,
        "run-sec-harmonization":7,
        "reload-harmonization-securitization-tables":8,
        "run-b3-securitization":9,
        "mdl-out-b3-with-securitization":10,
        "reload-securitization-tables-b3":11,
        "complete-strategic-batch-sec":12,
        "run-ler-securitization":13,
        "run-b3std-securitization":14,
        "run-lech-securitization":15,
        "run-lvr-securitization":16,
        "reload-securitization-tables-ler":17,
        "reload-securitization-tables-b3std":18,
        "reload-securitization-tables-lech":19,
        "reload-securitization-tables-lvr":20,
        "complete-b3-securitization-batch":21,
        "mdl-out-ler-with-securitization":22,
        "mdl-out-b3std-with-securitization":23,
        "mdl-out-lech-with-securitization":24,
        "mdl-out-lvr-with-securitization":25,
        "complete-securitization-batch":26,
        "reload-tactical-tables-post-securitization":27,
        "securitization-error-handler":28}

connection = (("complete-b3-strategic-batch", "skip-regional-batches"),
              ("skip-regional-batches", "init-securitization-batch"),
              ("init-securitization-batch", "start-securitization-batch"),
              ("start-securitization-batch", "run-sec-tactical-staging"),
              ("start-securitization-batch", "run-sec-harmonization"),
              ("run-sec-harmonization", "reload-harmonization-securitization-tables"),
              ("run-sec-tactical-staging", "run-b3-securitization"),
              ("run-sec-harmonization", "run-b3-securitization"),
              ("run-b3-securitization", "mdl-out-b3-with-securitization"),
              ("run-b3-securitization", "reload-securitization-tables-b3"),
              ("complete-strategic-batch", "complete-strategic-batch-sec"),
              ("run-b3-securitization", "run-ler-securitization"),
              ("run-b3-securitization", "run-b3std-securitization"),
              ("run-b3-securitization", "run-lech-securitization"),
              ("run-b3-securitization", "run-lvr-securitization"),
              ("run-ler-securitization", "reload-securitization-tables-ler"),
              ("run-b3std-securitization", "reload-securitization-tables-b3std"),
              ("run-lech-securitization", "reload-securitization-tables-lech"),
              ("run-lvr-securitization", "reload-securitization-tables-lvr"),
              ("mdl-out-b3-with-securitization", "complete-b3-securitization-batch"),
              ("run-ler-securitization", "mdl-out-ler-with-securitization"),
              ("run-b3std-securitization", "mdl-out-b3std-with-securitization"),
              ("run-lech-securitization", "mdl-out-lech-with-securitization"),
              ("run-lvr-securitization", "mdl-out-lvr-with-securitization"),
              ("complete-b3-securitization-batch", "complete-securitization-batch"),
              ("mdl-out-ler-with-securitization", "complete-securitization-batch"),
              ("mdl-out-b3std-with-securitization", "complete-securitization-batch"),
              ("mdl-out-lech-with-securitization", "complete-securitization-batch"),
              ("mdl-out-lvr-with-securitization", "complete-securitization-batch"),
              ("complete-b3-securitization-batch", "reload-tactical-tables-post-securitization"),
              ("complete-securitization-batch", "reload-tactical-tables-post-securitization"))

G = nx.DiGraph()
G.add_node("securitization-error-handler")
G.add_edges_from(connection)
pos = nx.kamada_kawai_layout(G, scale=1)
nx.draw_networkx_nodes(G,pos=jobs)
nx.draw_networkx_edges(G, jobs)
nx.draw_networkx_labels(G, jobs, Labels)
plt.savefig("securitization_flow_graph")
plt.show()
