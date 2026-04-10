function RUL = rul_prediction(failure_index, length_signal)

RUL = zeros(1, length_signal);

for i = 1:length_signal
    RUL(i) = failure_index - i;
end
