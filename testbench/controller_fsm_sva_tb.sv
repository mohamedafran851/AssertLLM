module controller_fsm_sva_tb;

    reg clk;
    reg reset;
    reg start;
    reg finish;

    wire busy;
    wire done;

    // Access the internal FSM state
    wire [1:0] state;

    // Tracks whether a previous clock sample exists
    reg past_valid;

    // DUT
    controller_fsm dut (
        .clk(clk),
        .reset(reset),
        .start(start),
        .finish(finish),
        .busy(busy),
        .done(done)
    );

    assign state = dut.state;

    // Clock generation
    initial clk = 0;
    always #5 clk = ~clk;

    // Previous-cycle validity
    initial past_valid = 0;

    always @(posedge clk)
        past_valid <= 1;

    // Include AI-generated assertions
    `include "controller_fsm_assertions.sv"

    // Test stimulus
    initial begin

        $display("===== AI-GENERATED FSM SVA TEST =====");

        reset = 1;
        start = 0;
        finish = 0;

        // Apply synchronous reset
        repeat (2) @(negedge clk);
        reset = 0;

        // IDLE -> BUSY
        start = 1;
        @(negedge clk);
        start = 0;

        // BUSY remains BUSY
        repeat (2) @(negedge clk);

        // BUSY -> DONE
        finish = 1;
        @(negedge clk);
        finish = 0;

        // DONE -> IDLE
        @(negedge clk);

        // IDLE remains IDLE
        repeat (2) @(negedge clk);

        // Test reset while operating in BUSY
        start = 1;
        @(negedge clk);
        start = 0;

        repeat (2) @(negedge clk);

        reset = 1;
        @(negedge clk);
        reset = 0;

        repeat (2) @(negedge clk);

        $display("===== FSM SVA TEST COMPLETED =====");
        $finish;

    end

endmodule
