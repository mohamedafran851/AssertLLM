module fsm_illegal_state_tb;

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

    property legal_state_property;
        @(posedge clk)
        past_valid |-> (state != 2'b11);
    endproperty

    assert property (legal_state_property);

    initial begin

        $display("===== ILLEGAL STATE DETECTION TEST =====");

        reset = 1;
        start = 0;
        finish = 0;

        repeat (2) @(negedge clk);
        reset = 0;

        // IDLE -> BUSY
        start = 1;
        @(negedge clk);
        start = 0;

        // BUSY -> DONE
        finish = 1;
        @(negedge clk);
        finish = 0;

        // DONE -> ILLEGAL STATE
        repeat (2) @(negedge clk);

        $display("ERROR: Illegal state was not detected.");
        $finish;

    end

endmodule
