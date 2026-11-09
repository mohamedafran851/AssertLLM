property alu_add_property;
@(posedge clk)
(ALU_Sel == 3'b000)
|->
({CarryOut, ALU_Out} == ({1'b0, A} + {1'b0, B}));
endproperty
assert property (alu_add_property);

property alu_sub_property;
@(posedge clk)
(ALU_Sel == 3'b001)
|->
({CarryOut, ALU_Out} == ({1'b0, A} - {1'b0, B}));
endproperty
assert property (alu_sub_property);

property alu_and_property;
@(posedge clk)
(ALU_Sel == 3'b010)
|->
(ALU_Out == (A & B)) && (CarryOut == 1'b0);
endproperty
assert property (alu_and_property);

property alu_or_property;
@(posedge clk)
(ALU_Sel == 3'b011)
|->
(ALU_Out == (A | B)) && (CarryOut == 1'b0);
endproperty
assert property (alu_or_property);

property alu_xor_property;
@(posedge clk)
(ALU_Sel == 3'b100)
|->
(ALU_Out == (A ^ B)) && (CarryOut == 1'b0);
endproperty
assert property (alu_xor_property);

property alu_not_property;
@(posedge clk)
(ALU_Sel == 3'b101)
|->
(ALU_Out == (~A)) && (CarryOut == 1'b0);
endproperty
assert property (alu_not_property);

property alu_invalid_property;
@(posedge clk)
((ALU_Sel == 3'b110) || (ALU_Sel == 3'b111))
|->
(ALU_Out == 4'b0000) && (CarryOut == 1'b0);
endproperty
assert property (alu_invalid_property);
