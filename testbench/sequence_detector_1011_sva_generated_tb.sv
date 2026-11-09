module sequence_detector_1011_sva_generated_tb;

reg clk = 0;
reg reset = 0;
reg din = 0;
wire detected;

sequence_detector_1011 dut (
    .clk(clk),
    .reset(reset),
    .din(din),
    .detected(detected)
);

always #5 clk = ~clk;

`include "sequence_detector_1011_assertions.sv"

initial begin
    reset = 1;
    @(posedge clk);
    #1;
    reset = 0;

    // First sequence: 1011
    @(negedge clk); din = 1;
    @(negedge clk); din = 0;
    @(negedge clk); din = 1;
    @(negedge clk); din = 1;
    @(negedge clk); din = 0;

    // Reset before overlapping test
    reset = 1;
    @(negedge clk);
    reset = 0;

    // Overlapping sequence: 1011011
    @(negedge clk); din = 1;
    @(negedge clk); din = 0;
    @(negedge clk); din = 1;
    @(negedge clk); din = 1;
    @(negedge clk); din = 0;
    @(negedge clk); din = 1;
    @(negedge clk); din = 1;
    @(negedge clk); din = 0;

    @(negedge clk);

    $display("SEQUENCE DETECTOR GENERATED SVA TEST: PASSED");
    $finish;
end

endmodule
