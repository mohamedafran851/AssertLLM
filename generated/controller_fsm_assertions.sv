property reset_property;
    @(posedge clk)
    reset |=> (state == 2'b00);
endproperty
assert property (reset_property);

property idle_transition_property;
    @(posedge clk)
    (past_valid && !$past(reset) &&
     $past(state) == 2'b00)
    |-> (($past(start) && state == 2'b01) ||
         (!$past(start) && state == 2'b00));
endproperty
assert property (idle_transition_property);

property busy_transition_property;
    @(posedge clk)
    (past_valid && !$past(reset) &&
     $past(state) == 2'b01)
    |-> (($past(finish) && state == 2'b10) ||
         (!$past(finish) && state == 2'b01));
endproperty
assert property (busy_transition_property);

property done_transition_property;
    @(posedge clk)
    (past_valid && !$past(reset) &&
     $past(state) == 2'b10)
    |-> (state == 2'b00);
endproperty
assert property (done_transition_property);

property output_property;
    @(posedge clk)
    (busy == (state == 2'b01)) &&
    (done == (state == 2'b10));
endproperty
assert property (output_property);
property legal_state_property;
    @(posedge clk)
    past_valid |-> (state != 2'b11);
endproperty

assert property (legal_state_property);
