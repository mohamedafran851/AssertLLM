// MANUAL ASSERTIONS FOR 4-BIT UP/DOWN COUNTER

// 1. Synchronous reset
property manual_reset_property;
    @(posedge clk)
    (past_valid && reset)
    |=> (count == 4'd0);
endproperty

assert property (manual_reset_property);


// 2. Increment when direction is 1
property manual_up_property;
    @(posedge clk)
    (past_valid && !$past(reset) && $past(direction))
    |-> (count == ($past(count) + 4'd1));
endproperty

assert property (manual_up_property);


// 3. Decrement when direction is 0
property manual_down_property;
    @(posedge clk)
    (past_valid && !$past(reset) && !$past(direction))
    |-> (count == ($past(count) - 4'd1));
endproperty

assert property (manual_down_property);
