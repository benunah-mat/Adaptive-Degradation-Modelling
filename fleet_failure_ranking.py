# ============================================================
# fleet_failure_ranking.py
# Fleet-level failure risk ranking
# ============================================================

import numpy as np


def fleet_failure_ranking(machines):

    num_machines  = len(machines)
    failure_times = np.zeros(num_machines)

    print("\n=== Fleet Failure Risk Ranking ===")

    for m in range(num_machines):
        ft = machines[m]['failure_time']
        failure_times[m] = ft if ft is not None else np.inf

    sorted_indices = np.argsort(failure_times)   # returns indices that would sort the array

    for rank, idx in enumerate(sorted_indices):
        machine_id = idx + 1   # display as 1-indexed for readability
        ft         = failure_times[idx]
        if ft == np.inf:
            print(f"Rank {rank+1} → Machine {machine_id} (No failure detected)")
        else:
            print(f"Rank {rank+1} → Machine {machine_id} (Failure Time: {int(ft)})")