clc;
clear;
close all;

%% Step 1: Set dataset folder path
folder_path = 'C:\Users\USER\Downloads\Projects\IMS\1st_test'; 

files = dir(folder_path);

% Remove '.' and '..'
files = files(~ismember({files.name},{'.','..'}));

num_files = length(files);

%% Step 2: Extract RMS vibration from each file

V = zeros(1, num_files);

for i = 1:num_files
    
    filename = fullfile(folder_path, files(i).name);
    
    data = load(filename);
    
    bearing_signal = data(:,6); % Bearing No.
    
    % Compute RMS vibration
    V(i) = rms(bearing_signal);
    
end

%% Step 3: Create time vector

t = 1:num_files;

%% Step 4: Convert vibration to health state

V0 = V(1);
Vfail = max(V);

H = (Vfail - V) / (Vfail - V0);

H(H > 1) = 1;
H(H < 0) = 0;

%% Step 5: Compute degradation rate

dt = 1;

dHdt = zeros(size(H));

for i = 1:length(H)-1
    dHdt(i) = (H(i+1) - H(i)) / dt;
end

%% Step 6: Plot results

figure;

subplot(2,1,1);
plot(t, V, 'LineWidth', 2);
xlabel('Time step');
ylabel('RMS Vibration');
title('Real Bearing Vibration (NASA Dataset)');
grid on;

subplot(2,1,2);
plot(t, H, 'LineWidth', 2);
xlabel('Time step');
ylabel('Health H(t)');
title('DHDE Health State (Real Data)');
grid on;

%% DHDE Structural Validation on Real Bearing Data

valid_indices = 1:length(dHdt)-1;

X = V(valid_indices);
Y = -dHdt(valid_indices);

% Remove invalid values
valid = X > 0 & Y > 0;

X = X(valid);
Y = Y(valid);

logX = log(X);
logY = log(Y);

% Linear regression
p = polyfit(logX, logY, 1);

m_est = p(1);
alpha_est = exp(p(2));

disp(['Estimated exponent m (real data): ', num2str(m_est)]);
disp(['Estimated alpha (real data): ', num2str(alpha_est)]);

% Plot validation
figure;
scatter(logX, logY);
hold on;
plot(logX, polyval(p, logX), 'r', 'LineWidth', 2);
xlabel('log(Vibration)');
ylabel('log(Degradation Rate)');
title('DHDE Structural Validation - Real Bearing Data');
grid on;

%% DHDE Failure Prediction

H_critical = 0.2;

failure_index = find(H <= H_critical, 1);

if ~isempty(failure_index)
    
    failure_time = t(failure_index);
    
    disp(['DHDE predicted failure time: ', num2str(failure_time)]);
    
else
    
    disp('Failure threshold not reached in dataset');
    
end

%% DHDE Prognostic Test Using Partial Data

% Choose percentage of life observed
life_fraction = 0.4;

cutoff_index = floor(life_fraction * length(H));

% Use only early data
t_partial = t(1:cutoff_index);
V_partial = V(1:cutoff_index);
H_partial = H(1:cutoff_index);

% Compute degradation rate for partial data
dHdt_partial = zeros(size(H_partial));

for i = 1:length(H_partial)-1
    dHdt_partial(i) = (H_partial(i+1) - H_partial(i));
end

% Estimate DHDE parameters from partial data
X = V_partial(1:end-1);
Y = -dHdt_partial(1:end-1);

valid = X > 0 & Y > 0;

logX = log(X(valid));
logY = log(Y(valid));

p = polyfit(logX, logY, 1);

m_est_partial = p(1);
alpha_est_partial = exp(p(2));

disp(['Partial-data estimated m: ', num2str(m_est_partial)]);
disp(['Partial-data estimated alpha: ', num2str(alpha_est_partial)]);

%% Predict failure time using estimated parameters

H_current = H_partial(end);

V_current = V_partial(end);

% Estimate degradation rate at current state
D_current = alpha_est_partial * V_current^m_est_partial;

% Estimate remaining life
remaining_steps = (H_current - 0.2) / D_current;

predicted_failure_time = cutoff_index + remaining_steps;

disp(['Predicted failure index from partial data: ', num2str(predicted_failure_time)]);

disp(['Actual failure index: ', num2str(failure_time)]);

prediction_error = abs(predicted_failure_time - failure_time);

disp(['Prediction error (index units): ', num2str(prediction_error)]);

%% Multi-stage DHDE Prognostic Validation

fractions = [0.4, 0.6, 0.8];

for k = 1:length(fractions)
    
    life_fraction = fractions(k);
    
    cutoff_index = floor(life_fraction * length(H));
    
    V_partial = V(1:cutoff_index);
    H_partial = H(1:cutoff_index);
    
    dHdt_partial = diff(H_partial);
    
    X = V_partial(1:end-1);
    Y = -dHdt_partial;
    
    valid = X > 0 & Y > 0;
    
    logX = log(X(valid));
    logY = log(Y(valid));
    
    p = polyfit(logX, logY, 1);
    
    m_est = p(1);
    alpha_est = exp(p(2));
    
    H_current = H_partial(end);
    V_current = V_partial(end);
    
    D_current = alpha_est * V_current^m_est;
    
    remaining_steps = (H_current - 0.2) / D_current;
    
    predicted_failure = cutoff_index + remaining_steps;
    
    error = abs(predicted_failure - failure_time);
    
    disp(['Life fraction: ', num2str(life_fraction)]);
    disp(['Predicted failure: ', num2str(predicted_failure)]);
    disp(['Error: ', num2str(error)]);
    disp(' ');
    
end

%% Adaptive DHDE

window_size = 200;
degradation_threshold = 1e-6;

% PREALLOCATE FIRST
m_adaptive = NaN(1, length(H)-window_size);

for i = 1:length(H)-window_size
    
    V_window = V(i:i+window_size);
    H_window = H(i:i+window_size);
    
    dHdt_window = diff(H_window);
    
    X = V_window(1:end-1);
    Y = -dHdt_window;
    
    valid = X > 0 & Y > degradation_threshold;
    
    if sum(valid) > 20
        
        p = polyfit(log(X(valid)), log(Y(valid)), 1);
        
        m_est = p(1);
        
        if m_est >= 0 && m_est <= 6
            m_adaptive(i) = m_est;
        end
        
    end
    
end

% Smooth result
m_adaptive = smoothdata(m_adaptive, 'movmean', 50);

figure;
plot(m_adaptive);
xlabel('Time index');
ylabel('Exponent m');
title('Physically Constrained Adaptive DHDE');
grid on;

num_nan = sum(isnan(m_adaptive));
total = length(m_adaptive);

disp(['Number of NaN values: ', num2str(num_nan)]);
disp(['Total values: ', num2str(total)]);
disp(['Percentage NaN: ', num2str(100*num_nan/total), '%']);

% Store raw adaptive before smoothing
m_adaptive_raw = m_adaptive;

% Smooth separately
m_adaptive = smoothdata(m_adaptive_raw, 'movmean', 50);

% Store raw adaptive exponent BEFORE smoothing
% (Make sure you defined m_adaptive_raw earlier like this:)
% m_adaptive_raw = m_adaptive;

% Find first valid exponent estimate from RAW adaptive array
first_valid_index = find(~isnan(m_adaptive_raw), 1);

% Display raw index (window-based index)
disp(['Raw DHDE observability index: ', num2str(first_valid_index)]);
disp(['Raw percentage of life: ', num2str(100*first_valid_index/length(H)), '%']);

% Correct for sliding window center offset
true_index = first_valid_index + floor(window_size/2);

disp(['Corrected DHDE observability index: ', num2str(true_index)]);
disp(['Corrected percentage of life: ', num2str(100*true_index/length(H)), '%']);

%% Visual confirmation plot

figure;
plot(m_adaptive_raw);
hold on;
xline(first_valid_index, 'r', 'LineWidth', 2);
xline(true_index, 'g', 'LineWidth', 2);

xlabel('Time index');
ylabel('Adaptive exponent m');
title('DHDE Observability Point');
legend('Adaptive exponent', 'Raw observability', 'Corrected observability');
grid on;

%% Real-time Adaptive DHDE Prognostics (Corrected)

predicted_failure_adaptive = NaN(1,length(H));

for t_index = window_size:length(m_adaptive_raw)+window_size-1
    
    adaptive_index = t_index - window_size + 1;
    
    m_current = m_adaptive_raw(adaptive_index);
    
    if ~isnan(m_current)
        
        V_window = V(adaptive_index:t_index);
        H_window = H(adaptive_index:t_index);
        
        dHdt_window = diff(H_window);
        
        X = V_window(1:end-1);
        Y = -dHdt_window;
        
        valid = X > 0 & Y > 1e-6;
        
        if sum(valid) > 20
            
            p = polyfit(log(X(valid)), log(Y(valid)), 1);
            
            alpha_current = exp(p(2));
            
            H_current = H(t_index);
            V_current = V(t_index);
            
            % THIS IS WHERE THE FIX GOES
            D_current = alpha_current * V_current^m_current;
            
            min_degradation_rate = 1e-6;
            
            if D_current > min_degradation_rate
                
                remaining_steps = (H_current - 0.2)/D_current;
                
                predicted_failure = t_index + remaining_steps;
                
                if predicted_failure <= length(H)*1.5
                    
                    predicted_failure_adaptive(t_index) = predicted_failure;
                    
                end
                
            end
            
        end
        
    end
    
end

figure;
plot(predicted_failure_adaptive);
hold on;
yline(failure_time,'r','Actual failure');
xlabel('Time index');
ylabel('Predicted failure index');
title('Real-Time Adaptive DHDE Failure Prediction');
grid on;

prediction_error = abs(predicted_failure_adaptive - failure_time);

figure;
plot(prediction_error);
xlabel('Time index');
ylabel('Prediction error');
title('Adaptive DHDE Prediction Error vs Time');
grid on;