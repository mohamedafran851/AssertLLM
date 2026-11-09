property reset_property;
    @(posedge clk)
    reset |=> (count == 4'd0);
endproperty
assert property (reset_property);

property increment_property;
    @(posedge clk)
    (past_valid && !$past(reset))
    |-> (count == ($past(count) + 4'd1));
endproperty
assert property (increment_property);

property overflow_property;
    @(posedge clk)
    (past_valid && !$past(reset) && $past(count) == 4'd15)
    |-> (count == 4'd0);
endproperty
assert property (overflow_property);
