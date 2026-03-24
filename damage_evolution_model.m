function D = damage_evolution_model(machine,t,dt,k,a,b,c,d)

gamma = 3;        % damage acceleration
sigma = 5e-5;     % noise intensity (tune this)

D = zeros(size(t));

for i = 2:length(t)

base_growth = k*(machine.Load^a) * ...
              (machine.Temperature^b) * ...
              (machine.Speed^c) * ...
              (machine.Lubrication^-d);

% deterministic + stochastic growth
stochastic_noise = sigma * randn;

growth = base_growth * (1 + gamma*D(i-1)) + stochastic_noise;

% ensure growth doesn't go negative
growth = max(growth, 0);

D(i) = D(i-1) + growth*dt;

% clamp bounds
D(i) = max(0, min(D(i),1));

if D(i) >= 1
    D(i:end) = 1;
    break
end

end

end
