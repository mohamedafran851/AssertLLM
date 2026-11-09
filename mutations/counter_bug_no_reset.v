module counter (
    input wire clk,
    input wire reset,
    output reg [3:0] count
);

always @(posedge clk) begin
    count <= count + 1'b1;
end

endmodule
