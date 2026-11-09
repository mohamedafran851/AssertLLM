property mux_sel_00_property; @(posedge clk) (Sel == 2'b00) |-> (Y == D[0]); endproperty
assert property (mux_sel_00_property);

property mux_sel_01_property; @(posedge clk) (Sel == 2'b01) |-> (Y == D[1]); endproperty
assert property (mux_sel_01_property);

property mux_sel_10_property; @(posedge clk) (Sel == 2'b10) |-> (Y == D[2]); endproperty
assert property (mux_sel_10_property);

property mux_sel_11_property; @(posedge clk) (Sel == 2'b11) |-> (Y == D[3]); endproperty
assert property (mux_sel_11_property);

