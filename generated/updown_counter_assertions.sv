property reset_property;
    @(posedge clk)
    reset |=> (count == 4'd0);
endproperty
assert property (reset_property);

property up_count_property;
    @(posedge clk)
    (past_valid && !$past(reset) && $past(direction))
    |-> (count == ($past(count) + 4'd1));
endproperty
assert property (up_count_property);

property down_count_property;
    @(posedge clk)
    (past_valid && !$past(reset) && !$past(direction))
    |-> (count == ($past(count) - 4'd1));
endproperty
assert property (down_count_property);
