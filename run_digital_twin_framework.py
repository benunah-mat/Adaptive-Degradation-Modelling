# ============================================================
# FAILURE SIMULATION FRAMEWORK FOR PREDICTIVE DIGITAL TWINS
# Main Execution Script
# ============================================================

import numpy as np
import matplotlib.pyplot as plt

from digital_twin_simulatorx import digital_twin_simulatorx
from fleet_failure_ranking   import fleet_failure_ranking
from monte_carlo_rul         import monte_carlo_rul

def main():

    print("Starting Failure Simulation Framework...")

    num_machines = 4
    t  = np.arange(1, 12001)
    dt = 1

    machines = digital_twin_simulatorx(num_machines, t, dt)
    fleet_failure_ranking(machines)

    print("\nSimulation Complete.")

    machine = machines[0]
    num_sim = 100
    k = 1e-4; a = 1.5; b = 1.2; c = 1.1; d = 1.3

    failure_times = monte_carlo_rul(machine, t, dt, k, a, b, c, d, num_sim)

    mean_tf  = np.mean(failure_times)
    std_tf   = np.std(failure_times)
    lower_95 = mean_tf - 2*std_tf
    upper_95 = mean_tf + 2*std_tf

    plt.figure()
    plt.hist(failure_times, bins=20)
    plt.xlabel('Failure Time')
    plt.ylabel('Frequency')
    plt.title('Failure Time Distribution with Confidence Interval')
    plt.grid(True)
    plt.axvline(mean_tf,  color='r', linewidth=2, linestyle='-',  label='Mean')
    plt.axvline(lower_95, color='g', linewidth=2, linestyle='--', label='Lower 95%')
    plt.axvline(upper_95, color='g', linewidth=2, linestyle='--', label='Upper 95%')
    plt.legend()

    print(f"\n=== Probabilistic RUL Results (Machine 1) ===")
    print(f"Mean Failure Time: {mean_tf:.2f}")
    print(f"Std Dev: {std_tf:.2f}")
    print(f"95% Confidence Interval: [{lower_95:.2f}, {upper_95:.2f}]")

    threshold_time = round(mean_tf)
    prob_failure   = np.sum(failure_times <= threshold_time) / len(failure_times)
    print(f"Probability of failure before {threshold_time}: {prob_failure:.2f}")

    sorted_times = np.sort(failure_times)
    cdf = np.arange(1, len(sorted_times) + 1) / len(sorted_times)

    plt.figure()
    plt.plot(sorted_times, cdf, linewidth=2)
    plt.xlabel('Time')
    plt.ylabel('Probability of Failure')
    plt.title('Failure Probability Curve (CDF)')
    plt.grid(True)

    plt.show()


if __name__ == "__main__":
    main()