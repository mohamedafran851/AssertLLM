module updown_counter_tb;

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

task check_count;
    input [3:0] expected;
    begin
        #1;
        if (count !== expected) begin
            $display("FAIL: Expected %0d, Got %0d",
                     expected, count);
            $finish;
        end
        else begin
            $display("PASS: Count = %0d", count);
        end
    end
endtask

initial begin
    $display("===== UP/DOWN COUNTER TEST =====");

    reset = 1;
    direction = 1;

    repeat (2) @(negedge clk);
    reset = 0;

    direction = 1;
    @(posedge clk);
    check_count(1);

    direction = 1;
    @(posedge clk);
    check_count(2);

    direction = 0;
    @(posedge clk);
    check_count(1);

    direction = 0;
    @(posedge clk);
    check_count(0);

    direction = 0;
    @(posedge clk);
    check_count(15);

    direction = 1;
    @(posedge clk);
    check_count(0);

    $display("===== ALL TESTS COMPLETED =====");
    $finish;
end

endmodule
