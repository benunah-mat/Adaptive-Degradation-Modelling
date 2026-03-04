%% ============================================================
% PHASE 1 — DHDE DETERMINISTIC DEGRADATION MODEL
% =============================================================
clc; clear; close all;

%% ---------------- DATA LOADING ----------------
folder_path = 'C:\Users\USER\Downloads\Projects\IMS\1st_test';

files = dir(folder_path);
files = files(~ismember({files.name},{'.','..'}));
num_files = length(files);

V = zeros(1, num_files);

for i = 1:num_files
    filename = fullfile(folder_path, files(i).name);
    data = load(filename);
    bearing_signal = data(:,6);     % Change if needed
    V(i) = rms(bearing_signal);
end

t = 1:num_files;

%% ---------------- HEALTH STATE TRANSFORMATION ----------------
V0 = V(1);
Vfail = max(V);

H = (Vfail - V) / (Vfail - V0);
H(H>1)=1; H(H<0)=0;

%% ---------------- DEGRADATION RATE ----------------
dHdt = diff(H);
V_trim = V(1:end-1);

%% ---------------- DHDE PARAMETER ESTIMATION ----------------
valid = V_trim>0 & -dHdt>1e-6;

X = V_trim(valid);
Y = -dHdt(valid);

logX = log(X);
logY = log(Y);

p = polyfit(logX, logY, 1);

m_est = p(1);
alpha_est = exp(p(2));

Y_fit = polyval(p, logX);
R2 = 1 - sum((logY - Y_fit).^2)/sum((logY - mean(logY)).^2);

fprintf('\n===== PHASE 1: DHDE PARAMETERS =====\n');
fprintf('m = %.4f\n', m_est);
fprintf('alpha = %.4f\n', alpha_est);
fprintf('R^2 = %.4f\n', R2);

%% ---------------- FAILURE DETECTION ----------------
H_critical = 0.2;
failure_index = find(H <= H_critical,1);

fprintf('Actual failure index: %d\n', failure_index);

%% ---------------- PLOTS ----------------
figure;
subplot(2,1,1);
plot(t,V,'LineWidth',2);
xlabel('Time'); ylabel('RMS Vibration');
title('Raw Vibration Signal');
grid on;

subplot(2,1,2);
plot(t,H,'LineWidth',2);
xlabel('Time'); ylabel('Health H(t)');
title('DHDE Health State');
grid on;

figure;
scatter(logX,logY); hold on;
plot(logX,Y_fit,'r','LineWidth',2);
xlabel('log(V)'); ylabel('log(dH/dt)');
title('DHDE Structural Validation');
grid on;
