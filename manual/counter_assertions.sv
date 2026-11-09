// MANUAL ASSERTIONS FOR 4-BIT COUNTER

// 1. Synchronous reset
property manual_reset_property;
    @(posedge clk)
    (past_valid && reset)
    |=> (count == 4'd0);
endproperty

assert property (manual_reset_property);


// 2. Counter increments by one
property manual_increment_property;
    @(posedge clk)
    (past_valid && !$past(reset))
    |-> (count == ($past(count) + 4'd1));
endproperty

assert property (manual_increment_property);


// 3. Counter wraps from 15 to 0
property manual_overflow_property;
    @(posedge clk)
    (past_valid && !$past(reset) &&
     $past(count) == 4'd15)
    |-> (count == 4'd0);
endproperty

assert property (manual_overflow_property);
