# ============================================================
# monte_carlo_rul.py
# Monte Carlo simulation for probabilistic RUL estimation
# ============================================================

import numpy as np
from damage_evolution_model import damage_evolution_model


def monte_carlo_rul(machine, t, dt, k, a, b, c, d, num_sim):

    failure_times = np.zeros(num_sim)

    for sim in range(num_sim):

        D = damage_evolution_model(machine, t, dt, k, a, b, c, d)

        indices = np.where(D >= 1)[0]

        if len(indices) > 0:
            failure_index = indices[0]
        else:
            failure_index = len(t)   # if no failure, use end of simulation

        failure_times[sim] = failure_index

    return failure_times