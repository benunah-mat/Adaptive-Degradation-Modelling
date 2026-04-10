# ============================================================
# vibration_sensor_model.py
# Synthetic vibration signal generator
# ============================================================

import numpy as np


def vibration_sensor_model(D):

    V0          = 0.2
    beta        = 3
    m           = 2
    noise_level = 0.02

    V     = V0 + beta * (D ** m)
    noise = noise_level * np.random.randn(len(D))
    V     = V + noise

    return V