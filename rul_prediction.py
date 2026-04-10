# ============================================================
# rul_prediction.py
# Deterministic Remaining Useful Life prediction
# ============================================================

import numpy as np


def rul_prediction(failure_index, length_signal):

    RUL = np.zeros(length_signal)

    for i in range(length_signal):
        RUL[i] = failure_index - i

    return RUL