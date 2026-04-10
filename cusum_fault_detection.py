# ============================================================
# cusum_fault_detection.py
# CUSUM-based fault detection on RMS signal
# ============================================================

import numpy as np


def cusum_fault_detection(RMS_signal):

    mu0   = np.mean(RMS_signal[:20])   # baseline from first 20 windows
    k     = 0.01
    CUSUM = np.zeros(len(RMS_signal))

    for i in range(1, len(RMS_signal)):
        CUSUM[i] = max(0, CUSUM[i-1] + RMS_signal[i] - mu0 - k)

    threshold = 0.5
    indices   = np.where(CUSUM > threshold)[0]   # find all indices above threshold

    fault_index = indices[0] if len(indices) > 0 else None

    return fault_index