%% ============================================================
% PHASE 2 — ADAPTIVE EXPONENTIAL GROWTH MODEL
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
    bearing_signal = data(:,6);
    V(i) = rms(bearing_signal);
end

t = 1:num_files;
failure_index = find(V >= max(V)*0.99,1);

%% ---------------- SMOOTH VIBRATION ----------------
V_smooth = smoothdata(V,'movmean',20);

%% ---------------- LOG-GROWTH RATE ----------------
logV = log(V_smooth);
lambda = diff(logV);

%% ---------------- SLIDING WINDOW REGRESSION ----------------
window_size = 200;
lambda_est = NaN(1,length(V)-window_size);

for k = 1:length(lambda_est)
    
    idx_start = k;
    idx_end = k + window_size - 1;
    
    t_win = t(idx_start:idx_end);
    V_win = V_smooth(idx_start:idx_end);
    
    if any(V_win<=0)
        continue;
    end
    
    logV_win = log(V_win);
    
    p = polyfit(t_win,logV_win,1);
    lambda_est(k) = p(1);
    
end

%% ---------------- FAILURE PROJECTION ----------------
V_failure = max(V_smooth);
prediction = NaN(1,length(lambda_est));

for k = 1:length(lambda_est)
    
    lambda_k = lambda_est(k);
    
    if isnan(lambda_k) || lambda_k<=0
        continue;
    end
    
    t_current = k + window_size - 1;
    
    logA_est = logV(t_current) - lambda_k*t_current;
    t_fail_est = (log(V_failure) - logA_est)/lambda_k;
    
    if t_fail_est > t_current
        prediction(k) = t_fail_est;
    end
end

%% ---------------- RESULTS ----------------
fprintf('\n===== PHASE 2: ADAPTIVE EXPONENTIAL MODEL =====\n');
fprintf('Actual failure index: %d\n', failure_index);

figure;
plot(lambda_est,'LineWidth',1.5);
xlabel('Time Index');
ylabel('Estimated \lambda');
title('Adaptive Log-Growth Rate');
grid on;

figure;
plot(prediction); hold on;
yline(failure_index,'r','Actual Failure');
xlabel('Time');
ylabel('Predicted Failure Index');
title('Short-Horizon Exponential Prediction');
grid on;
