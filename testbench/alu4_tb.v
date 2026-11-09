module alu4_tb;

reg [3:0] A;
reg [3:0] B;
reg [2:0] ALU_Sel;

wire [3:0] ALU_Out;
wire CarryOut;

integer errors;

alu4 uut (
    .A(A),
    .B(B),
    .ALU_Sel(ALU_Sel),
    .ALU_Out(ALU_Out),
    .CarryOut(CarryOut)
);

task check_result;
    input [3:0] expected_out;
    input expected_carry;

    begin
        #1;

        if (ALU_Out !== expected_out ||
            CarryOut !== expected_carry) begin

            $display("FAIL: A=%d B=%d Sel=%b Output=%d Carry=%b Expected=%d Carry=%b",
                     A, B, ALU_Sel, ALU_Out, CarryOut,
                     expected_out, expected_carry);

            errors = errors + 1;

        end
        else begin
            $display("PASS: A=%d B=%d Sel=%b Output=%d Carry=%b",
                     A, B, ALU_Sel, ALU_Out, CarryOut);
        end
    end
endtask

initial begin

    errors = 0;

    $display("===== ASSERTLLM ALU TESTING =====");

    // Addition
    A = 4'd9; B = 4'd7; ALU_Sel = 3'b000;
    check_result(4'd0, 1'b1);

    // Normal addition
    A = 4'd3; B = 4'd4; ALU_Sel = 3'b000;
    check_result(4'd7, 1'b0);

    // Subtraction
    A = 4'd9; B = 4'd7; ALU_Sel = 3'b001;
    check_result(4'd2, 1'b0);

    // Subtraction underflow
    A = 4'd3; B = 4'd5; ALU_Sel = 3'b001;
    check_result(4'd14, 1'b1);

    // AND
    A = 4'b1100; B = 4'b1010; ALU_Sel = 3'b010;
    check_result(4'b1000, 1'b0);

    // OR
    A = 4'b1100; B = 4'b1010; ALU_Sel = 3'b011;
    check_result(4'b1110, 1'b0);

    // XOR
    A = 4'b1100; B = 4'b1010; ALU_Sel = 3'b100;
    check_result(4'b0110, 1'b0);

    // NOT
    A = 4'b1010; B = 4'b0000; ALU_Sel = 3'b101;
    check_result(4'b0101, 1'b0);

    // Invalid operation
    A = 4'd9; B = 4'd3; ALU_Sel = 3'b110;
    check_result(4'b0000, 1'b0);

    $display("--------------------------------");
    $display("Total errors: %0d", errors);

    if (errors == 0)
        $display("ALU TEST RESULT: PASSED");
    else
        $display("ALU TEST RESULT: FAILED");

    $finish;

end

endmodule
