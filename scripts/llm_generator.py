from pathlib import Path
import json
from llm_client import generate

PROJECT_DIR = Path(__file__).resolve().parent.parent

rtl_file = PROJECT_DIR / "rtl" / "counter.v"
spec_file = PROJECT_DIR / "prompts" / "counter_spec.txt"

rtl_code = rtl_file.read_text()
specification = spec_file.read_text()

print("===== AssertLLM Lesson 43 =====")
print("RTL loaded!")
print("Specification loaded!")

prompt = f"""
You are an expert SystemVerilog Design Verification Engineer.

Generate exactly THREE complete SystemVerilog assertions
for the following RTL design.

RTL:
{rtl_code}

SPECIFICATION:
{specification}

DESIGN:
- Module: counter
- Clock: clk
- Reset: synchronous active-high
- Count: 4-bit unsigned
- Reset value: 0
- Increment: 1 per clock when reset is low
- Overflow: 15 wraps to 0

TESTBENCH SIGNAL:
- past_valid starts at 0.
- past_valid becomes 1 after the first positive clock edge.

REQUIRED ASSERTIONS:

1. RESET:
   If reset is high, count must be zero at the next clock sample.
   Use |=>.

2. INCREMENT:
nano scripts/llm_generator.py   If the previous cycle was valid and previous reset was low,
   current count must equal previous count plus 4'd1.
   Use $past(count), $past(reset), and past_valid.

3. OVERFLOW:
   If the previous cycle was valid, previous reset was low,
   and previous count was 4'd15,
   current count must equal 4'd0.
STRICT SYSTEMVERILOG SYNTAX:

RESET PROPERTY:
property reset_property;
    @(posedge clk)
    reset |=> (count == 4'd0);
endproperty
assert property (reset_property);

INCREMENT PROPERTY:
property increment_property;
    @(posedge clk)
    (past_valid && !$past(reset))
    |-> (count == ($past(count) + 4'd1));
endproperty
assert property (increment_property);

OVERFLOW PROPERTY:
property overflow_property;
    @(posedge clk)
    (past_valid && !$past(reset) && $past(count) == 4'd15)
    |-> (count == 4'd0);
endproperty
assert property (overflow_property);

RULES:
- Follow these three syntax patterns exactly.
- Do not replace |-> or |=> with if statements.
- Do not change property names.
- Do not omit the word property in assert property (...).
- Write assert property (property_name) else $error("message");
- NEVER put a semicolon between assert property (...) and else.
- The else clause must be on the same assertion statement.
- Return valid JSON only.
- Include exactly three assertion objects with name and code.
"""
print("\nGenerating assertions using the selected LLM...")

raw_response = generate(prompt)

try:
    data = json.loads(raw_response)

    assertions = data["assertions"]

    if not isinstance(assertions, list) or len(assertions) != 3:
        raise ValueError("Expected exactly three assertions.")

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

        assertion_codes.append(code.strip())

    output_file = PROJECT_DIR / "generated" / "counter_assertions.sv"
    report_file = PROJECT_DIR / "reports" / "counter_llm_response.json"

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
