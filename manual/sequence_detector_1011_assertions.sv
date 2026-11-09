
property sequence_1011_detected;
    @(posedge clk)
    disable iff (reset)
    (dut.state == 3'b011 && din)
    |=> detected;
endproperty

assert property (sequence_1011_detected);

property detected_matches_state;
    @(posedge clk)
    (detected == (dut.state == 3'b100));
endproperty

assert property (detected_matches_state);

