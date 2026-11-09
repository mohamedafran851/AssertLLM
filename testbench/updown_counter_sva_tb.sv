module updown_counter_sva_tb;

    reg clk;
    reg reset;
    reg direction;
    wire [3:0] count;

    updown_counter dut (
        .clk(clk),
        .reset(reset),
        .direction(direction),
        .count(count)
    );

    initial clk = 0;
    always #5 clk = ~clk;

    bit past_valid = 0;

    always @(posedge clk)
        past_valid <= 1;

    `include "updown_counter_assertions.sv"

    initial begin
        $display("===== AI-GENERATED UP/DOWN SVA TEST =====");

        reset = 1;
        direction = 1;

        repeat (2) @(negedge clk);

        reset = 0;
        direction = 1;

        repeat (20) @(negedge clk);

        direction = 0;
        repeat (20) @(negedge clk);

        direction = 1;
        repeat (20) @(negedge clk);

        $display("===== AI-GENERATED UP/DOWN SVA TEST COMPLETED =====");
        $finish;
    end

endmodule
