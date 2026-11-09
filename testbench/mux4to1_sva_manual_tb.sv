module mux4to1_sva_manual_tb;

reg clk;
reg [3:0] D;
reg [1:0] Sel;
wire Y;

mux4to1 dut (
    .D(D),
    .Sel(Sel),
    .Y(Y)
);

initial clk = 0;
always #5 clk = ~clk;

`include "mux4to1_assertions.sv"

initial begin
    $display("===== MUX MANUAL SVA TEST =====");

    D = 4'b0001; Sel = 2'b00;
    @(negedge clk);

    D = 4'b0010; Sel = 2'b01;
    @(negedge clk);

    D = 4'b0100; Sel = 2'b10;
    @(negedge clk);

    D = 4'b1000; Sel = 2'b11;
    @(negedge clk);

    D = 4'b1111; Sel = 2'b00;
    @(negedge clk);

    D = 4'b0000; Sel = 2'b01;
    @(negedge clk);

    D = 4'b1010; Sel = 2'b10;
    @(negedge clk);

    D = 4'b0101; Sel = 2'b11;
    @(negedge clk);

    repeat (2) @(negedge clk);

    $display("MANUAL SVA TEST COMPLETED");
    $finish;
end

endmodule
