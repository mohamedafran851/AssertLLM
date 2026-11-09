module multiplier4_tb;

reg [3:0] A, B;
wire [7:0] Product;

integer errors = 0;

multiplier4 dut (
    .A(A),
    .B(B),
    .Product(Product)
);

task check;
    input [3:0] a;
    input [3:0] b;
    input [7:0] expected;
    begin
        A = a;
        B = b;
        #10;

        if (Product !== expected) begin
            $display("FAIL: A=%0d B=%0d Product=%0d Expected=%0d",
                     A, B, Product, expected);
            errors = errors + 1;
        end
        else begin
            $display("PASS: %0d * %0d = %0d", A, B, Product);
        end
    end
endtask

initial begin
    $display("===== 4-BIT MULTIPLIER TEST =====");

    check(0, 0, 0);
    check(2, 3, 6);
    check(5, 4, 20);
    check(7, 8, 56);
    check(10, 10, 100);
    check(15, 15, 225);
    check(15, 0, 0);
    check(1, 15, 15);

    if (errors == 0)
        $display("ALL TESTS PASSED");
    else
        $display("TESTS FAILED: %0d errors", errors);

    $finish;
end

endmodule
