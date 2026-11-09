module controller_fsm (
    input wire clk,
    input wire reset,
    input wire start,
    input wire finish,
    output wire busy,
    output wire done
);

    // State encoding
    parameter IDLE = 2'b00;
    parameter BUSY = 2'b01;
    parameter DONE = 2'b10;

    reg [1:0] state;
    reg [1:0] next_state;

    // State register
    always @(posedge clk) begin
        if (reset)
            state <= IDLE;
        else
            state <= next_state;
    end

    // Next-state logic
    always @(*) begin
        case (state)

            IDLE: begin
                if (start)
                    next_state = BUSY;
                else
                    next_state = IDLE;
            end

            BUSY: begin
                if (finish)
                    next_state = DONE;
                else
                    next_state = BUSY;
            end

            DONE: begin
                next_state = DONE;
            end

            default: begin
                next_state = IDLE;
            end

        endcase
    end

    // Moore output logic
    assign busy = (state == BUSY);
    assign done = (state == DONE);

endmodule
