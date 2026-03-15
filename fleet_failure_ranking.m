function fleet_failure_ranking(machines)

num_machines = length(machines);

fprintf('\n=== Fleet Failure Risk Ranking ===\n')

failure_times = zeros(1,num_machines);

for m = 1:num_machines
failure_times(m) = machines(m).failure_time;
end

[sorted_times,idx] = sort(failure_times);

for i = 1:num_machines

machine_id = idx(i);

fprintf('Rank %d → Machine %d (Failure Time: %d)\n', ...
    i,machine_id,sorted_times(i));


end
