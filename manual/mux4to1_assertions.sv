
// MANUAL ASSERTIONS FOR 4:1 MULTIPLEXER

property mux_sel_00;
    @(posedge clk)
    (Sel == 2'b00) |-> (Y == D[0]);
endproperty
assert property (mux_sel_00);

property mux_sel_01;
    @(posedge clk)
    (Sel == 2'b01) |-> (Y == D[1]);
endproperty
assert property (mux_sel_01);

property mux_sel_10;
    @(posedge clk)
    (Sel == 2'b10) |-> (Y == D[2]);
endproperty
assert property (mux_sel_10);

property mux_sel_11;
    @(posedge clk)
    (Sel == 2'b11) |-> (Y == D[3]);
endproperty
assert property (mux_sel_11);

