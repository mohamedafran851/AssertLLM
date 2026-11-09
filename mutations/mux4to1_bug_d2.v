module mux4to1 (
    input wire [3:0] D,
    input wire [1:0] Sel,
    output reg Y
);
always @(*) begin
    case (Sel)
        2'b00: Y = D[0];
        2'b01: Y = D[1];
        2'b10: Y = D[3];
        2'b11: Y = D[3];
    endcase
end
endmodule
