function fault_index = cusum_fault_detection(RMS_signal)

mu0 = mean(RMS_signal(1:20));
k   = 0.01;

CUSUM = zeros(size(RMS_signal));

for i = 2:length(RMS_signal)
    CUSUM(i) = max(0, CUSUM(i-1) + RMS_signal(i) - mu0 - k);
end

threshold   = 0.5;
fault_index = find(CUSUM > threshold, 1);
