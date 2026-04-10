# ============================================================
# digital_twin_simulatorx.py
# Multi-asset digital twin simulator — full pipeline
# ============================================================

import numpy as np
import matplotlib.pyplot as plt

from damage_evolution_model import damage_evolution_model
from vibration_sensor_model import vibration_sensor_model
from rms_health_indicator   import rms_health_indicator
from cusum_fault_detection  import cusum_fault_detection
from rul_prediction         import rul_prediction


def digital_twin_simulatorx(num_machines, t, dt):

    k = 1e-4
    a = 1.5
    b = 1.2
    c = 1.1
    d = 1.3

    machines = []   # Python list — equivalent to MATLAB struct array

    plt.figure()

    for m in range(num_machines):

        # Randomize operating conditions
        machine = {
            'Load'        : 1 + 0.5 * np.random.rand(),
            'Temperature' : 1 + 0.3 * np.random.rand(),
            'Speed'       : 1.0,
            'Lubrication' : 0.7 + 0.3 * np.random.rand(),
        }

        # Damage evolution
        D = damage_evolution_model(machine, t, dt, k, a, b, c, d)
        machine['Damage'] = D

        failure_indices        = np.where(D >= 1)[0]
        machine['failure_time'] = failure_indices[0] if len(failure_indices) > 0 else None

        # Vibration sensor
        V = vibration_sensor_model(D)
        machine['Vibration'] = V

        # RMS health indicator
        RMS = rms_health_indicator(V)
        machine['RMS'] = RMS

        # CUSUM fault detection
        fault_idx = cusum_fault_detection(RMS)
        machine['fault_index'] = fault_idx

        # Deterministic RUL prediction
        failure_time = machine['failure_time']
        if fault_idx is not None and failure_time is not None:
            window_size = 50
            failure_win = min(int(failure_time) // window_size, len(RMS))
            RUL = rul_prediction(failure_win, len(RMS))
            machine['RUL'] = RUL
        else:
            machine['RUL'] = np.array([])

        machines.append(machine)

        plt.plot(t, D, linewidth=2, label=f'Machine {m+1}')

    plt.xlabel('Time')
    plt.ylabel('Damage State')
    plt.title('Multi-Asset Digital Twin Simulation')
    plt.grid(True)

    return machines