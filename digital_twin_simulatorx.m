function machines = digital_twin_simulatorx(num_machines,t,dt)

k = 1e-4;

a = 1.5;
b = 1.2;
c = 1.1;
d = 1.3;

machines = struct();

figure
hold on

for m = 1:num_machines

machines(m).Load = 1 + 0.5*rand;
machines(m).Temperature = 1 + 0.3*rand;
machines(m).Speed = 1;
machines(m).Lubrication = 0.7 + 0.3*rand;

D = damage_evolution_model(machines(m),t,dt,k,a,b,c,d);

machines(m).Damage = D;

machines(m).failure_time = find(D==1,1);

V = vibration_sensor_model(D);

machines(m).Vibration = V;

plot(t,D,'LineWidth',2)

end

xlabel('Time')
ylabel('Damage State')
title('Multi-Asset Digital Twin Simulation')
grid on
