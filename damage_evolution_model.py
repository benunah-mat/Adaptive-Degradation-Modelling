# ============================================================
# damage_evolution_model.py
# Physics-based stochastic damage evolution model
# ============================================================

import numpy as np


def damage_evolution_model(machine, t, dt, k, a, b, c, d):

    gamma = 3       # damage acceleration factor
    sigma = 5e-5    # noise intensity

    D = np.zeros(len(t))

    for i in range(1, len(t)):

        base_growth = (k
                       * (machine['Load']        ** a)
                       * (machine['Temperature'] ** b)
                       * (machine['Speed']       ** c)
                       * (machine['Lubrication'] ** -d))

        stochastic_noise = sigma * np.random.randn()

        growth = base_growth * (1 + gamma * D[i-1]) + stochastic_noise
        growth = max(growth, 0)     # prevent negative growth

        D[i] = D[i-1] + growth * dt
        D[i] = max(0, min(D[i], 1))   # clamp between 0 and 1

        if D[i] >= 1:
            D[i:] = 1
            break

    return D