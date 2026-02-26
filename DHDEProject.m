clc;
clear;
close all;

%% Step 1: Time definition
dt = 1;                      % time step (hours)
t = 0:dt:500;                % total operating time
n = length(t);

%% Step 2: Simulate bearing vibration data
% Baseline vibration
V0 = 0.2;

% Failure vibration threshold
Vfail = 1.0;

% Simulate realistic vibration increase (accelerating degradation)
V = V0 + 0.0005*t + 0.000002*t.^2;

% Add small noise to simulate real sensor behavior
noise = 0.01*randn(size(t));
V = V + noise;

%% Step 3: Compute Health State using DHDE definition

H = (Vfail - V) / (Vfail - V0);

% Ensure health stays within bounds
H(H > 1) = 1;
H(H < 0) = 0;

%% Step 4: Compute degradation rate dH/dt

dHdt = zeros(1,n);

for i = 1:n-1
    dHdt(i) = (H(i+1) - H(i)) / dt;
end

%% Step 5: Define failure threshold

H_critical = 0.2;

failure_index = find(H <= H_critical, 1);

if ~isempty(failure_index)
    failure_time = t(failure_index);
    disp(['Predicted failure time: ', num2str(failure_time), ' hours']);
else
    disp('Failure not reached within simulation');
end

%% Step 6: Plot results

figure;

subplot(3,1,1);
plot(t, V, 'LineWidth', 2);
xlabel('Time (hours)');
ylabel('Vibration');
title('Bearing Vibration vs Time');
grid on;

subplot(3,1,2);
plot(t, H, 'LineWidth', 2);
hold on;
yline(H_critical, 'r--', 'Failure Threshold');
xlabel('Time (hours)');
ylabel('Health H(t)');
title('DHDE Health State vs Time');
grid on;

subplot(3,1,3);
plot(t, dHdt, 'LineWidth', 2);
xlabel('Time (hours)');
ylabel('Degradation Rate dH/dt');
title('DHDE Degradation Rate');
grid on;

%% Step 7: Test DHDE structure (power law test)

% Remove last element to match sizes
valid_indices = 1:n-1;

Y = -dHdt(valid_indices);   % degradation rate
X = V(valid_indices);       % vibration

% Remove negative/zero values for log fitting
valid = Y > 0 & X > 0;
Y = Y(valid);
X = X(valid);

% Take log to test power relationship
logX = log(X);
logY = log(Y);

% Linear regression in log space
p = polyfit(logX, logY, 1);

m_estimated = p(1);
alpha_estimated = exp(p(2));

disp(['Estimated exponent m: ', num2str(m_estimated)]);
disp(['Estimated alpha: ', num2str(alpha_estimated)]);

% Plot log-log relationship
figure;
scatter(logX, logY);
hold on;
plot(logX, polyval(p, logX), 'r', 'LineWidth', 2);
xlabel('log(Vibration)');
ylabel('log(Degradation Rate)');
title('DHDE Power Law Validation');
grid on;