module sequence_detector_1011 (
    input wire clk,
    input wire reset,
    input wire din,
    output reg detected
);

localparam S0 = 3'b000;
localparam S1 = 3'b001;
localparam S2 = 3'b010;
localparam S3 = 3'b011;
localparam S4 = 3'b100;

reg [2:0] state, next_state;

always @(posedge clk) begin
    if (reset)
        state <= S0;
    else
        state <= next_state;
end

always @(*) begin
    next_state = S0;

    case (state)
        S0: next_state = din ? S1 : S0;
        S1: next_state = din ? S1 : S2;
        S2: next_state = din ? S3 : S0;

        // BUG: Should enter S4 when din is 1
        S3: next_state = din ? S1 : S2;

        S4: next_state = din ? S1 : S2;
        default: next_state = S0;
    endcase
end

always @(*) begin
    detected = (state == S4);
end

endmodule
