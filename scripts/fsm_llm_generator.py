from pathlib import Path
import json
from llm_client import generate

PROJECT_DIR = Path(__file__).resolve().parent.parent

rtl_file = PROJECT_DIR / "rtl" / "controller_fsm.v"
spec_file = PROJECT_DIR / "prompts" / "controller_fsm_spec.txt"

rtl_code = rtl_file.read_text()
specification = spec_file.read_text()

print("===== AssertLLM FSM Assertion Generator =====")
print("RTL loaded!")
print("Specification loaded!")

prompt = f"""
You are an expert SystemVerilog Design Verification Engineer.

Generate exactly FIVE SystemVerilog assertions
for the following 3-state Moore FSM.

RTL:
{rtl_code}

SPECIFICATION:
{specification}

TESTBENCH SIGNALS:
- clk
- reset
- start
- finish
- busy
- done
- state: a 2-bit wire connected to dut.state.
- past_valid starts at 0 and becomes 1 after
  the first positive clock edge.

STATE ENCODINGS:
IDLE = 2'b00
BUSY = 2'b01
DONE = 2'b10

Generate these five properties:

1. RESET:
   If reset is high, state must become IDLE
   at the next clock sample.
   Use |=>.

2. IDLE TRANSITIONS:
   If the previous state was IDLE:
   - If previous start was 1, current state must be BUSY.
   - If previous start was 0, current state must remain IDLE.
   Use $past and |->.

3. BUSY TRANSITIONS:
   If the previous state was BUSY:
   - If previous finish was 1, current state must be DONE.
   - If previous finish was 0, current state must remain BUSY.
   Use $past and |->.

4. DONE TRANSITION:
   If the previous state was DONE,
   current state must be IDLE.
   Use $past and |->.

5. OUTPUTS:
   Verify that busy is 1 exactly when state is BUSY,
   and done is 1 exactly when state is DONE.

STRICT SYNTAX PATTERNS:

RESET:
property reset_property;
    @(posedge clk)
    reset |=> (state == 2'b00);
endproperty
assert property (reset_property);

IDLE:
property idle_transition_property;
    @(posedge clk)
    (past_valid && !$past(reset) &&
     $past(state) == 2'b00)
    |-> (($past(start) && state == 2'b01) ||
         (!$past(start) && state == 2'b00));
endproperty
assert property (idle_transition_property);

BUSY:
property busy_transition_property;
    @(posedge clk)
    (past_valid && !$past(reset) &&
     $past(state) == 2'b01)
    |-> (($past(finish) && state == 2'b10) ||
         (!$past(finish) && state == 2'b01));
endproperty
assert property (busy_transition_property);

DONE:
property done_transition_property;
    @(posedge clk)
    (past_valid && !$past(reset) &&
     $past(state) == 2'b10)
    |-> (state == 2'b00);
endproperty
assert property (done_transition_property);

OUTPUTS:
property output_property;
    @(posedge clk)
    (busy == (state == 2'b01)) &&
    (done == (state == 2'b10));
endproperty
assert property (output_property);

RULES:
- Generate exactly five assertion objects.
- Use exactly the five property names shown above.
- Follow the syntax patterns.
- Use valid SystemVerilog syntax.
- Return valid JSON only.
- Each assertion object must contain name and code.
- Do not use Markdown fences or explanations.
"""

print("\nGenerating FSM assertions using local Ollama...")

raw_response = generate(prompt)

try:
    data = json.loads(raw_response)
    assertions = data["assertions"]

    expected_names = {
        "reset_property",
        "idle_transition_property",
        "busy_transition_property",
        "done_transition_property",
        "output_property"
    }

    if not isinstance(assertions, list) or len(assertions) != 5:
        raise ValueError("Expected exactly five assertions.")

    received_names = set()
    assertion_codes = []

    for item in assertions:
        if not isinstance(item, dict):
            raise ValueError("Invalid assertion entry.")

        name = item.get("name")
        code = item.get("code")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Assertion name missing.")

        if not isinstance(code, str) or not code.strip():
            raise ValueError(f"Assertion code missing: {name}")

        received_names.add(name.strip())

        if f"property {name};" not in code:
            raise ValueError(f"Property declaration missing: {name}")

        if f"assert property ({name})" not in code:
            raise ValueError(f"Assertion statement missing: {name}")

        assertion_codes.append(code.strip())

    if received_names != expected_names:
        raise ValueError(
            f"Expected {expected_names}, received {received_names}"
        )

    output_file = (
        PROJECT_DIR / "generated" / "controller_fsm_assertions.sv"
    )

    report_file = (
        PROJECT_DIR / "reports" / "controller_fsm_llm_response.json"
    )

    output_file.parent.mkdir(exist_ok=True)
    report_file.parent.mkdir(exist_ok=True)

    report_file.write_text(json.dumps(data, indent=4))
    output_file.write_text("\n\n".join(assertion_codes) + "\n")

    print("\nJSON parsing successful!")
    print("Assertions generated:", len(assertion_codes))
    print("Generated SVA:", output_file)
    print("AI response:", report_file)

except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
    print("\nAI OUTPUT VALIDATION FAILED!")
    print("Reason:", error)
    print("Previous assertion file was not overwritten.")
    raise SystemExit(1)
