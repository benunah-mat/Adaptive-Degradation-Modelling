%% ============================================================
% FAILURE SIMULATION FRAMEWORK FOR PREDICTIVE DIGITAL TWINS
% Main Execution Script (Corrected - Full Pipeline)
% ============================================================

clc
clear
close all

fprintf('Starting Failure Simulation Framework...\n')

num_machines = 4;
t  = 1:12000;
dt = 1;

%% --- Step 1: Run Multi-Asset Digital Twin Simulation ---
machines = digital_twin_simulatorx(num_machines, t, dt);

%% --- Step 2: Fleet Failure Risk Ranking ---
fleet_failure_ranking(machines)

fprintf('\nSimulation Complete.\n')

%% ============================================================
% PROBABILISTIC RUL ANALYSIS (Machine 1)
% ============================================================

machine = machines(1);
num_sim = 100;
k = 1e-4;
a = 1.5;
b = 1.2;
c = 1.1;
d = 1.3;

%% --- Step 3: Monte Carlo RUL Simulation ---
failure_times = monte_carlo_rul(machine, t, dt, k, a, b, c, d, num_sim);

%% Compute statistics
mean_tf  = mean(failure_times);
std_tf   = std(failure_times);

%% --- Step 4: Confidence Interval ---
lower_95 = mean_tf - 2*std_tf;
upper_95 = mean_tf + 2*std_tf;

%% Plot failure time distribution
figure
histogram(failure_times, 20)
xlabel('Failure Time')
ylabel('Frequency')
title('Failure Time Distribution with Confidence Interval')
grid on
hold on
xline(mean_tf,   'r',   'LineWidth', 2, 'Label', 'Mean')
xline(lower_95,  'g--', 'LineWidth', 2, 'Label', 'Lower 95%')
xline(upper_95,  'g--', 'LineWidth', 2, 'Label', 'Upper 95%')

fprintf("\n=== Probabilistic RUL Results (Machine 1) ===\n")
fprintf("Mean Failure Time: %.2f\n",  mean_tf)
fprintf("Std Dev: %.2f\n",            std_tf)
fprintf("95%% Confidence Interval: [%.2f, %.2f]\n", lower_95, upper_95)

threshold_time = round(mean_tf);
prob_failure   = sum(failure_times <= threshold_time) / length(failure_times);
fprintf("Probability of failure before %d: %.2f\n", threshold_time, prob_failure)

%% --- Step 5: CDF (Failure Probability Curve) ---
sorted_times = sort(failure_times);
cdf = (1:length(sorted_times)) / length(sorted_times);

figure
plot(sorted_times, cdf, 'LineWidth', 2)
xlabel('Time')
ylabel('Probability of Failure')
title('Failure Probability Curve (CDF)')
grid on
