from pathlib import Path
import json
from llm_client import generate

PROJECT_DIR = Path(__file__).resolve().parent.parent

rtl_file = PROJECT_DIR / "rtl" / "updown_counter.v"
spec_file = PROJECT_DIR / "prompts" / "updown_counter_spec.txt"

rtl_code = rtl_file.read_text()
specification = spec_file.read_text()

print("===== AssertLLM Up/Down Counter Generator =====")
print("RTL loaded!")
print("Specification loaded!")

prompt = f"""
You are an expert SystemVerilog Design Verification Engineer.

Generate exactly THREE complete SystemVerilog assertions
for this 4-bit synchronous up/down counter.

RTL:
{rtl_code}

SPECIFICATION:
{specification}

TESTBENCH SIGNAL:
- past_valid starts at 0.
- past_valid becomes 1 after the first positive clock edge.

Generate these three properties:

1. RESET:
   If reset is high, count must be zero at the next clock sample.
   Use |=>.

2. UP COUNT:
   If the previous cycle was valid, previous reset was low,
   and previous direction was 1, current count must equal
   previous count plus 4'd1.
   Use $past(count), $past(reset), $past(direction),
   and past_valid.

3. DOWN COUNT:
   If the previous cycle was valid, previous reset was low,
   and previous direction was 0, current count must equal
   previous count minus 4'd1.
   Use $past(count), $past(reset), $past(direction),
   and past_valid.

STRICT SYNTAX:

RESET:
property reset_property;
    @(posedge clk)
    reset |=> (count == 4'd0);
endproperty
assert property (reset_property);

UP COUNT:
property up_count_property;
    @(posedge clk)
    (past_valid && !$past(reset) && $past(direction))
    |-> (count == ($past(count) + 4'd1));
endproperty
assert property (up_count_property);

DOWN COUNT:
property down_count_property;
    @(posedge clk)
    (past_valid && !$past(reset) && !$past(direction))
    |-> (count == ($past(count) - 4'd1));
endproperty
assert property (down_count_property);

RULES:
- Follow the three syntax patterns exactly.
- Do not change the property names.
- Use |=> for reset and |-> for up/down counting.
- Use 4-bit arithmetic so overflow and underflow wrap naturally.
- Return valid JSON only.
- Include exactly three assertion objects with name and code.
- Do not include Markdown fences or explanations.
"""

print("\nGenerating assertions using the local LLM...")

raw_response = generate(prompt)

try:
    data = json.loads(raw_response)
    assertions = data["assertions"]

    expected_names = {
        "reset_property",
        "up_count_property",
        "down_count_property"
    }

    if not isinstance(assertions, list) or len(assertions) != 3:
        raise ValueError("Expected exactly three assertions.")

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
        assertion_codes.append(code.strip())

    if received_names != expected_names:
        raise ValueError(
            f"Expected names {expected_names}, received {received_names}"
        )

    output_file = (
        PROJECT_DIR / "generated" / "updown_counter_assertions.sv"
    )
    report_file = (
        PROJECT_DIR / "reports" / "updown_counter_llm_response.json"
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
