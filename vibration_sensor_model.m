function V = vibration_sensor_model(D)

V0 = 0.2;
beta = 3;
m = 2;

V = V0 + beta*(D.^m);

noise_level = 0.02;

noise = noise_level*randn(size(V));

V = V + noise;
