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

machine = machines(1);   % select machine

num_sim = 100;

k = 1e-4;
a = 1.5;
b = 1.2;
c = 1.1;
d = 1.3;

failure_times = monte_carlo_rul(machine,t,dt,k,a,b,c,d,num_sim);

figure
histogram(failure_times,20)
xlabel('Failure Time')
ylabel('Frequency')
title('Failure Time Distribution')
grid on

mean_tf = mean(failure_times);
std_tf = std(failure_times);

fprintf("Mean Failure Time: %.2f\n",mean_tf);
fprintf("Std Dev: %.2f\n",std_tf);

