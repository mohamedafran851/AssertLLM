module alu4_sva_manual_tb;

reg clk;

reg [3:0] A;
reg [3:0] B;
reg [2:0] ALU_Sel;

wire [3:0] ALU_Out;
wire CarryOut;

alu4 uut (
    .A(A),
    .B(B),
    .ALU_Sel(ALU_Sel),
    .ALU_Out(ALU_Out),
    .CarryOut(CarryOut)
);

// Clock generation
initial clk = 0;
always #5 clk = ~clk;

// Include manual assertions
`include "alu4_assertions.sv"

// Apply inputs away from the assertion sampling edge
task apply_operation;
    input [3:0] test_A;
    input [3:0] test_B;
    input [2:0] test_Sel;

    begin
        @(negedge clk);

        A = test_A;
        B = test_B;
        ALU_Sel = test_Sel;

        @(posedge clk);
        #1;

        $display("TEST: A=%d B=%d Sel=%b Output=%d Carry=%b",
                 A, B, ALU_Sel, ALU_Out, CarryOut);
    end
endtask

initial begin

    A = 0;
    B = 0;
    ALU_Sel = 0;

    $display("===== ALU MANUAL ASSERTION TEST =====");

    apply_operation(4'd9, 4'd7, 3'b000);
    apply_operation(4'd3, 4'd4, 3'b000);

    apply_operation(4'd9, 4'd7, 3'b001);
    apply_operation(4'd3, 4'd5, 3'b001);

    apply_operation(4'b1100, 4'b1010, 3'b010);
    apply_operation(4'b1100, 4'b1010, 3'b011);
    apply_operation(4'b1100, 4'b1010, 3'b100);

    apply_operation(4'b1010, 4'b0000, 3'b101);

    apply_operation(4'd9, 4'd3, 3'b110);
    apply_operation(4'd9, 4'd3, 3'b111);

    $display("===== ALU MANUAL ASSERTION TEST COMPLETED =====");

    $finish;
end

endmodule
