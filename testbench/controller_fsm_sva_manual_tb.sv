module controller_fsm_sva_manual_tb;

    reg clk;
    reg reset;
    reg start;
    reg finish;

    wire busy;
    wire done;
    wire [1:0] state;

    reg past_valid;

    controller_fsm dut (
        .clk(clk),
        .reset(reset),
        .start(start),
        .finish(finish),
        .busy(busy),
        .done(done)
    );

    assign state = dut.state;

    initial clk = 0;
    always #5 clk = ~clk;

    initial past_valid = 0;

    always @(posedge clk)
        past_valid <= 1;

    `include "controller_fsm_assertions.sv"

    initial begin

        $display("===== MANUAL FSM SVA TEST =====");

        reset = 1;
        start = 0;
        finish = 0;

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

        // Enter BUSY again
        start = 1;
        @(negedge clk);
        start = 0;

        repeat (2) @(negedge clk);

        // Reset while BUSY
        reset = 1;
        @(negedge clk);
        reset = 0;

        repeat (2) @(negedge clk);

        $display("===== MANUAL FSM SVA TEST COMPLETED =====");
        $finish;

    end

endmodule
