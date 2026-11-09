`timescale 1ns/1ps

module counter_tb;

    reg clk;
    reg reset;
    wire [3:0] count;

    // Instantiate the counter
    counter uut (
        .clk(clk),
        .reset(reset),
        .count(count)
    );

    // Generate clock
    always #5 clk = ~clk;

    initial begin

        clk = 0;
        reset = 1;

        $dumpfile("counter.vcd");
        $dumpvars(0, counter_tb);

        $monitor("Time=%0t Reset=%b Count=%d",
                  $time, reset, count);

        // Apply reset
        #10;
        @(negedge clk);
        reset = 0;

        // Check counter values
        repeat (5) begin
            @(posedge clk);
            #1;
        end

        if (count == 5)
            $display("TEST PASSED");
        else
            $display("TEST FAILED");

        $finish;

    end

endmodule
