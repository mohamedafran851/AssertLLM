module counter_sva_tb;

    reg clk;
    reg reset;
    wire [3:0] count;

    // Instantiate the original counter
    counter dut (
        .clk(clk),
        .reset(reset),
        .count(count)
    );

    // Clock generation: 10 ns period
    initial clk = 0;
    always #5 clk = ~clk;

    // Tracks whether a previous clock sample exists
    bit past_valid = 0;

    always @(posedge clk)
        past_valid <= 1;

    // --------------------------------
    // ASSERTION 1: SYNCHRONOUS RESET
    // --------------------------------
    property counter_reset;
        @(posedge clk)
        reset |=> (count == 4'd0);
    endproperty

    assert property (counter_reset)
        else $error("RESET ASSERTION FAILED");

    // --------------------------------
    // ASSERTION 2: INCREMENT BY ONE
    // --------------------------------
    property counter_increment;
        @(posedge clk)
        (past_valid && !$past(reset))
        |-> (count == ($past(count) + 4'd1));
    endproperty

    assert property (counter_increment)
        else $error("INCREMENT ASSERTION FAILED");

    // --------------------------------
    // ASSERTION 3: OVERFLOW
    // --------------------------------
    property counter_overflow;
        @(posedge clk)
        (past_valid && !$past(reset) &&
         $past(count) == 4'd15)
        |-> (count == 4'd0);
    endproperty

    assert property (counter_overflow)
        else $error("OVERFLOW ASSERTION FAILED");

    // --------------------------------
    // TEST SEQUENCE
    // --------------------------------
    initial begin

        $display("===== AssertLLM SVA TEST =====");

        reset = 1;

        repeat (2) @(negedge clk);

        reset = 0;

        // Run enough cycles to test overflow
        repeat (20) @(negedge clk);

        $display("===== TEST COMPLETED =====");

        $finish;

    end

endmodule
