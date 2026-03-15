function RMS_signal = rms_health_indicator(V_sensor)

window_size = 50;

num_windows = floor(length(V_sensor)/window_size);

RMS_signal = zeros(1,num_windows);

for i = 1:num_windows

idx_start = (i-1)*window_size + 1;
idx_end = i*window_size;

segment = V_sensor(idx_start:idx_end);

RMS_signal(i) = rms(segment);


end
