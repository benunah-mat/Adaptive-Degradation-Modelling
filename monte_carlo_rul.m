function failure_times = monte_carlo_rul(machine,t,dt,k,a,b,c,d,num_sim)

failure_times = zeros(1,num_sim);

for sim = 1:num_sim

    D = damage_evolution_model(machine,t,dt,k,a,b,c,d);

    failure_index = find(D>=1,1);

    if isempty(failure_index)
        failure_index = length(t);
    end

    failure_times(sim) = failure_index;

end

end
