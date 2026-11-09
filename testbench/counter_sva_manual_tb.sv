module counter_sva_manual_tb;

    reg clk;
    reg reset;
    wire [3:0] count;

    counter dut (
        .clk(clk),
        .reset(reset),
        .count(count)
    );

    initial clk = 0;
    always #5 clk = ~clk;

    bit past_valid = 0;

    always @(posedge clk)
        past_valid <= 1;

    `include "counter_assertions.sv"

    initial begin
        $display("===== MANUAL COUNTER SVA TEST =====");

        reset = 1;

        repeat (2) @(negedge clk);

        reset = 0;

        repeat (20) @(negedge clk);

        $display("===== MANUAL COUNTER SVA TEST COMPLETED =====");
        $finish;
    end

endmodule
