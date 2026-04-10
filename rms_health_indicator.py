# ============================================================
# rms_health_indicator.py
# RMS-based health indicator from vibration signal
# ============================================================

import numpy as np


def rms_health_indicator(V_sensor):

    window_size = 50
    num_windows = len(V_sensor) // window_size   # // is integer division in Python
    RMS_signal  = np.zeros(num_windows)

    for i in range(num_windows):
        idx_start       = i * window_size
        idx_end         = idx_start + window_size
        segment         = V_sensor[idx_start:idx_end]
        RMS_signal[i]   = np.sqrt(np.mean(segment ** 2))

    return RMS_signal