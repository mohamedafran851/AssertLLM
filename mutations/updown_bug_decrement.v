module updown_counter (
    input wire clk,
    input wire reset,
    input wire direction,
    output reg [3:0] count
);

always @(posedge clk) begin
    if (reset)
        count <= 4'd0;
    else if (direction)
        count <= count + 1'b1;
    else
        count <= count - 2'b10;
end

endmodule
