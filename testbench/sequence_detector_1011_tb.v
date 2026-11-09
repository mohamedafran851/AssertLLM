`timescale 1ns/1ps

module sequence_detector_1011_tb;

reg clk;
reg reset;
reg din;
wire detected;

integer errors = 0;

sequence_detector_1011 dut (
    .clk(clk),
    .reset(reset),
    .din(din),
    .detected(detected)
);

always #5 clk = ~clk;

task send_bit;
    input bit_value;
    input expected;
    begin
        @(negedge clk);
        din = bit_value;

        @(posedge clk);
        #1;

        if (detected !== expected) begin
            $display("FAIL: din=%b expected=%b got=%b",
                     bit_value, expected, detected);
            errors = errors + 1;
        end
        else begin
            $display("PASS: din=%b detected=%b",
                     bit_value, detected);
        end
    end
endtask

initial begin
    clk = 0;
    reset = 1;
    din = 0;

    // Apply synchronous reset
    @(posedge clk);
    #1;
    if (detected !== 0) errors = errors + 1;

    @(negedge clk);
    reset = 0;

    $display("\\nTEST 1: Detect 1011");
    send_bit(1, 0);
    send_bit(0, 0);
    send_bit(1, 0);
    send_bit(1, 1);

    $display("\\nTEST 2: Detect overlapping 1011011");
    reset = 1;
    @(posedge clk);
    #1;
    @(negedge clk);
    reset = 0;

    send_bit(1, 0);
    send_bit(0, 0);
    send_bit(1, 0);
    send_bit(1, 1);
    send_bit(0, 0);
    send_bit(1, 0);
    send_bit(1, 1);

    $display("\\nTEST 3: No detection for 0000");
    reset = 1;
    @(posedge clk);
    #1;
    @(negedge clk);
    reset = 0;

    send_bit(0, 0);
    send_bit(0, 0);
    send_bit(0, 0);
    send_bit(0, 0);

    $display("\\n================================");
    if (errors == 0)
        $display("SEQUENCE DETECTOR TEST: PASSED");
    else
        $display("SEQUENCE DETECTOR TEST: FAILED (%0d errors)", errors);
    $display("================================");

    $finish;
end

endmodule
