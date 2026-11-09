module alu4 (
    input  wire [3:0] A,
    input  wire [3:0] B,
    input  wire [2:0] ALU_Sel,

    output reg  [3:0] ALU_Out,
    output reg        CarryOut
);

always @(*) begin

    ALU_Out = 4'b0000;
    CarryOut = 1'b0;

    case (ALU_Sel)

        3'b000: begin
            {CarryOut, ALU_Out} = A + B;
        end

        3'b001: begin
            {CarryOut, ALU_Out} = A - B;
        end

        3'b010: begin
            ALU_Out = A & B;
        end

        3'b011: begin
            ALU_Out = A | B;
        end

        3'b100: begin
            ALU_Out = A ^ B;
        end

        3'b101: begin
            ALU_Out = ~A;
        end

        default: begin
            ALU_Out = 4'b0000;
            CarryOut = 1'b0;
        end

    endcase

end

endmodule
