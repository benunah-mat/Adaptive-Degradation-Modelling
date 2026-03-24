%% ============================================================
% FAILURE SIMULATION FRAMEWORK FOR PREDICTIVE DIGITAL TWINS
% Main Execution Script
% ============================================================

clc
clear
close all

fprintf('Starting Failure Simulation Framework...\n')

num_machines = 4;
t = 1:12000;
dt = 1;

machines = digital_twin_simulatorx(num_machines,t,dt);

fleet_failure_ranking(machines)

fprintf('\nSimulation Complete.\n')

%% ============================================================
% PROBABILISTIC RUL ANALYSIS
% ============================================================

machine = machines(1);   % choose machine

num_sim = 100;

k = 1e-4;
a = 1.5;
b = 1.2;
c = 1.1;
d = 1.3;

failure_times = monte_carlo_rul(machine,t,dt,k,a,b,c,d,num_sim);

%% Histogram

figure
histogram(failure_times,20)
xlabel('Failure Time')
ylabel('Frequency')
title('Failure Time Distribution')
grid on

%% Statistics

mean_tf = mean(failure_times);
std_tf = std(failure_times);

fprintf("Mean Failure Time: %.2f\n",mean_tf);
fprintf("Std Dev: %.2f\n",std_tf);

%% Probability of failure before a threshold

threshold_time = round(mean_tf);

prob_failure = sum(failure_times <= threshold_time) / length(failure_times);

fprintf("Probability of failure before %d: %.2f\n", threshold_time, prob_failure);

%% CDF (Failure Probability Curve)

sorted_times = sort(failure_times);

cdf = (1:length(sorted_times)) / length(sorted_times);

figure
plot(sorted_times, cdf, 'LineWidth',2)

xlabel('Time')
ylabel('Probability of Failure')
title('Failure Probability Curve (CDF)')
grid on
