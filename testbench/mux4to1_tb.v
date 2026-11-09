module mux4to1_tb;

reg [3:0] D;
reg [1:0] Sel;
wire Y;

integer errors = 0;

mux4to1 dut (
    .D(D),
    .Sel(Sel),
    .Y(Y)
);

task check;
    input [3:0] data;
    input [1:0] select;
    input expected;
    begin
        D = data;
        Sel = select;
        #10;

        if (Y !== expected) begin
            $display("FAIL: D=%b Sel=%b Y=%b Expected=%b",
                     D, Sel, Y, expected);
            errors = errors + 1;
        end
        else begin
            $display("PASS: D=%b Sel=%b Y=%b",
                     D, Sel, Y);
        end
    end
endtask

initial begin
    $display("===== 4:1 MUX TEST =====");

    check(4'b0001, 2'b00, 1'b1);
    check(4'b0010, 2'b01, 1'b1);
    check(4'b0100, 2'b10, 1'b1);
    check(4'b1000, 2'b11, 1'b1);

    check(4'b1111, 2'b00, 1'b1);
    check(4'b0000, 2'b01, 1'b0);
    check(4'b1010, 2'b10, 1'b0);
    check(4'b0101, 2'b11, 1'b0);

    if (errors == 0)
        $display("ALL TESTS PASSED");
    else
        $display("TESTS FAILED: %0d errors", errors);

    $finish;
end

endmodule
