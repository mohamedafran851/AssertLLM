`timescale 1ns/1ps

module controller_fsm_tb;

    reg clk;
    reg reset;
    reg start;
    reg finish;

    wire busy;
    wire done;

    controller_fsm dut (
        .clk(clk),
        .reset(reset),
        .start(start),
        .finish(finish),
        .busy(busy),
        .done(done)
    );

    // Clock generation
    initial clk = 0;
    always #5 clk = ~clk;

    // Test procedure
    initial begin

        $display("===== FSM TEST STARTED =====");

        // Test 1: Reset
        reset = 1;
        start = 0;
        finish = 0;

        @(posedge clk);
        #1;

        if (busy == 0 && done == 0)
            $display("PASS: Reset -> IDLE");
        else
            $display("FAIL: Reset");

        // Test 2: IDLE -> BUSY
        reset = 0;
        start = 1;

        @(posedge clk);
        #1;

        if (busy == 1 && done == 0)
            $display("PASS: IDLE -> BUSY");
        else
            $display("FAIL: IDLE -> BUSY");

        // Test 3: Remain in BUSY
        start = 0;
        finish = 0;

        @(posedge clk);
        #1;

        if (busy == 1 && done == 0)
            $display("PASS: BUSY remains BUSY");
        else
            $display("FAIL: BUSY hold");

        // Test 4: BUSY -> DONE
        finish = 1;

        @(posedge clk);
        #1;

        if (busy == 0 && done == 1)
            $display("PASS: BUSY -> DONE");
        else
            $display("FAIL: BUSY -> DONE");

        // Test 5: DONE -> IDLE
        finish = 0;

        @(posedge clk);
        #1;

        if (busy == 0 && done == 0)
            $display("PASS: DONE -> IDLE");
        else
            $display("FAIL: DONE -> IDLE");

        $display("===== FSM TEST COMPLETED =====");

        $finish;
    end

endmodule
