// MANUAL ASSERTIONS FOR 4-BIT ALU

// 1. Addition
property manual_alu_add_property;
    @(posedge clk)
    (ALU_Sel == 3'b000)
    |->
    ({CarryOut, ALU_Out} ==
     ({1'b0, A} + {1'b0, B}));
endproperty

assert property (manual_alu_add_property);


// 2. Subtraction
property manual_alu_sub_property;
    @(posedge clk)
    (ALU_Sel == 3'b001)
    |->
    ({CarryOut, ALU_Out} ==
     ({1'b0, A} - {1'b0, B}));
endproperty

assert property (manual_alu_sub_property);


// 3. AND operation
property manual_alu_and_property;
    @(posedge clk)
    (ALU_Sel == 3'b010)
    |->
    (ALU_Out == (A & B) && CarryOut == 1'b0);
endproperty

assert property (manual_alu_and_property);


// 4. OR operation
property manual_alu_or_property;
    @(posedge clk)
    (ALU_Sel == 3'b011)
    |->
    (ALU_Out == (A | B) && CarryOut == 1'b0);
endproperty

assert property (manual_alu_or_property);


// 5. XOR operation
property manual_alu_xor_property;
    @(posedge clk)
    (ALU_Sel == 3'b100)
    |->
    (ALU_Out == (A ^ B) && CarryOut == 1'b0);
endproperty

assert property (manual_alu_xor_property);


// 6. NOT operation
property manual_alu_not_property;
    @(posedge clk)
    (ALU_Sel == 3'b101)
    |->
    (ALU_Out == (~A) && CarryOut == 1'b0);
endproperty

assert property (manual_alu_not_property);


// 7. Invalid operation
property manual_alu_invalid_property;
    @(posedge clk)
    (ALU_Sel == 3'b110 || ALU_Sel == 3'b111)
    |->
    (ALU_Out == 4'b0000 && CarryOut == 1'b0);
endproperty

assert property (manual_alu_invalid_property);
