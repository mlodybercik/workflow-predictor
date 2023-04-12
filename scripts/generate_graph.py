import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')


jobs_secure = {"complete-b3-strategic-batch":(0,0),
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

Labels_secure = {"complete-b3-strategic-batch":1,
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

connection_secure = (("complete-b3-strategic-batch", "skip-regional-batches"),
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
G.add_edges_from(connection_secure)

nx.draw_networkx_nodes(G,pos=jobs_secure)
nx.draw_networkx_edges(G, jobs_secure)
nx.draw_networkx_labels(G, jobs_secure, Labels_secure)
plt.savefig("securitization_flow_graph")
plt.show()

jobs_strat = {"f1-notification-trigger":(0,0),  #1
                "open-date-card":(2,0), #2
                "init-strategic-batch":(4,0),   #3
                "start-strategic-batch":(6,0),  #4
                "land-f1ref-data": (8,0),   #5
                "land-f1mdl-data": (8,2),   #6
                "reload-f1mdl-landing-tables":(10,4),   #7
                "reload-f1ref-landing-tables":(10,0),   #8
                "run-data-staging":(10,2),  #9
                "reload-staging-tables":(12,0), #10
                "run-data-harmonization":(12,2),    #11
                "reload-harmonized-reference-tables":(14,0),    #12
                "reload-product-audit":(14,4),  #13
                "reload-harmonized-non-reference-tables":(16,2),    #14
                "complete-strategic-harmonization-job":(14,2),  #15
                "run-b3-calculation":(16,0),    #16
                "b3-calc-completed": (18,2),    #17
                "run-b3std-calculation":(20,-2), #18
                "run-b3ler-calculation":(22,-2), #19
                "run-b3lech-calculation":(18,0),    #20
                "run-b3lvr-calculation":(18,4), #21
                "strategic-calc-completed":(24,-6),  #22
                "mdl-out-b3":(20,0),    #23
                "complete-b3-strategic-batch":(24,1),   #24
                "mdl-out-ler":(26,-4),   #25
                "mdl-out-b3std":(20,-8), #26
                "mdl-out-lech":(26,-2),  #27
                "mdl-out-lvr":(24,4),   #28
                "reload-b3-tables":(22,2),  #29
                "reload-b3std-tables":(26,1),   #30
                "reload-b3ler-tables":(30,-3),   #31
                "reload-b3lech-tables":(28,0),  #32
                "run-collateral-utilization":(28,4),    #33
                "reload-collateral-utilization":(32,6), #34
                "reload-b3-audit":(32,2),   #35
                "reload-b3std-audit":(34,6),    #36
                "reload-b3ler-audit":(36,2),    #37
                "reload-b3lech-audit":(38,6),   #38
                "reload-b3lvr-tables":(36,0),   #39
                "reload-b3lvr-audit":(38,2),    #40
                "complete-strategic-batch":(40,-4)} #41

connection_strat = (
            ("f1-notification-trigger","open-date-card"),
            ("open-date-card","init-strategic-batch"),
            ("init-strategic-batch","start-strategic-batch"),
            ("start-strategic-batch","land-f1ref-data"),
            ("start-strategic-batch","land-f1mdl-data"),
            ("land-f1mdl-data","reload-f1mdl-landing-tables"),
            ("land-f1ref-data","reload-f1ref-landing-tables"),
            ("land-f1mdl-data","run-data-staging"),
            ("land-f1ref-data","run-data-staging"),
            ("run-data-staging","reload-staging-tables"),
            ("run-data-staging","run-data-harmonization"),
            ("run-data-harmonization","reload-harmonized-reference-tables"),
            ("run-data-harmonization","reload-product-audit"),
            ("reload-harmonized-reference-tables","reload-harmonized-non-reference-tables"),
            ("run-data-harmonization","complete-strategic-harmonization-job"),
            ("complete-strategic-harmonization-job","run-b3-calculation"),
            ("run-b3-calculation","b3-calc-completed"),
            ("reload-harmonized-reference-tables","b3-calc-completed"),
            ("run-b3-calculation","run-b3std-calculation"),
            ("run-b3-calculation","run-b3ler-calculation"),
            ("run-b3-calculation","run-b3lech-calculation"),
            ("run-b3-calculation","run-b3lvr-calculation"),
            ("run-b3ler-calculation","strategic-calc-completed"),
            ("run-b3lech-calculation","strategic-calc-completed"),
            ("run-b3std-calculation","strategic-calc-completed"),
            ("b3-calc-completed","mdl-out-b3"),
            ("mdl-out-b3","complete-b3-strategic-batch"),
            ("run-b3ler-calculation","mdl-out-ler"),
            ("run-b3std-calculation","mdl-out-b3std"),
            ("run-b3lech-calculation","mdl-out-lech"),
            ("run-b3lvr-calculation","mdl-out-lvr"),
            ("b3-calc-completed","reload-b3-tables"),
            ("run-b3std-calculation","reload-b3std-tables"),
            ("run-b3ler-calculation","reload-b3ler-tables"),
            ("run-b3lech-calculation","reload-b3lech-tables"),
            ("run-b3-calculation","run-collateral-utilization"),
            ("run-b3ler-calculation","run-collateral-utilization"),
            ("run-b3std-calculation","run-collateral-utilization"),
            ("run-b3lech-calculation","run-collateral-utilization"),
            ("run-collateral-utilization","reload-collateral-utilization"),
            ("reload-b3-tables","reload-b3-audit"),
            ("reload-b3std-tables","reload-b3std-audit"),
            ("reload-b3-audit","reload-b3std-audit"),
            ("reload-b3ler-tables","reload-b3ler-audit"),
            ("reload-b3std-audit","reload-b3ler-audit"),
            ("reload-b3lech-tables","reload-b3lech-audit"),
            ("reload-b3ler-audit","reload-b3lech-audit"),
            ("run-b3lvr-calculation","reload-b3lvr-tables"),
            ("reload-b3lvr-tables","reload-b3lvr-audit"),
            ("mdl-out-b3","complete-strategic-batch"),
            ("mdl-out-ler","complete-strategic-batch"),
            ("mdl-out-b3std","complete-strategic-batch"),
            ("mdl-out-lech","complete-strategic-batch"))

Labels_strat = {"f1-notification-trigger":1,
                "open-date-card":2,
                "init-strategic-batch":3,
                "start-strategic-batch":4,
                "land-f1ref-data":5,
                "land-f1mdl-data":6,
                "reload-f1mdl-landing-tables":7,
                "reload-f1ref-landing-tables":8,
                "run-data-staging":9,
                "reload-staging-tables":10,
                "run-data-harmonization":11,
                "reload-harmonized-reference-tables":12,
                "reload-product-audit":13,
                "reload-harmonized-non-reference-tables":14,
                "complete-strategic-harmonization-job":15,
                "run-b3-calculation":16,
                "b3-calc-completed":17,
                "run-b3std-calculation":18,
                "run-b3ler-calculation":19,
                "run-b3lech-calculation":20,
                "run-b3lvr-calculation":21,
                "strategic-calc-completed":22,
                "mdl-out-b3":23,
                "complete-b3-strategic-batch":24,
                "mdl-out-ler":25,
                "mdl-out-b3std":26,
                "mdl-out-lech":27,
                "mdl-out-lvr":28,
                "reload-b3-tables":29,
                "reload-b3std-tables":30,
                "reload-b3ler-tables":31,
                "reload-b3lech-tables":32,
                "run-collateral-utilization":33,
                "reload-collateral-utilization":34,
                "reload-b3-audit":35,
                "reload-b3std-audit":36,
                "reload-b3ler-audit":37,
                "reload-b3lech-audit":38,
                "reload-b3lvr-tables":39,
                "reload-b3lvr-audit":40,
                "complete-strategic-batch":41}

G = nx.DiGraph()
G.add_edges_from(connection_strat)

nx.draw_networkx_nodes(G,pos=jobs_strat)
nx.draw_networkx_edges(G, jobs_strat)
nx.draw_networkx_labels(G, jobs_strat, Labels_strat)
plt.savefig("strategic_flow_graph")
plt.show()