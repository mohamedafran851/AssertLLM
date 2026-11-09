// MANUAL ASSERTIONS FOR 3-STATE MOORE FSM

// 1. Synchronous reset to IDLE
property manual_reset_property;
    @(posedge clk)
    (past_valid && reset)
    |=> (state == 2'b00);
endproperty

assert property (manual_reset_property);


// 2. IDLE transition
property manual_idle_property;
    @(posedge clk)
    (past_valid && !$past(reset) &&
     $past(state) == 2'b00)
    |-> (($past(start) && state == 2'b01) ||
         (!$past(start) && state == 2'b00));
endproperty

assert property (manual_idle_property);


// 3. BUSY transition
property manual_busy_property;
    @(posedge clk)
    (past_valid && !$past(reset) &&
     $past(state) == 2'b01)
    |-> (($past(finish) && state == 2'b10) ||
         (!$past(finish) && state == 2'b01));
endproperty

assert property (manual_busy_property);


// 4. DONE returns to IDLE
property manual_done_property;
    @(posedge clk)
    (past_valid && !$past(reset) &&
     $past(state) == 2'b10)
    |-> (state == 2'b00);
endproperty

assert property (manual_done_property);


// 5. Moore output checking
property manual_output_property;
    @(posedge clk)
    (busy == (state == 2'b01)) &&
    (done == (state == 2'b10));
endproperty

assert property (manual_output_property);


// 6. Illegal-state checking
property manual_legal_state_property;
    @(posedge clk)
    past_valid |-> (state != 2'b11);
endproperty

assert property (manual_legal_state_property);
