from pathlib import Path
import json
from llm_client import generate

PROJECT_DIR = Path(__file__).resolve().parent.parent

rtl_file = PROJECT_DIR / "rtl" / "sequence_detector_1011.v"
spec_file = PROJECT_DIR / "prompts" / "sequence_detector_1011_spec.txt"
prompt_file = PROJECT_DIR / "prompts" / "sequence_detector_1011_llm_prompt.txt"

rtl_code = rtl_file.read_text()
specification = spec_file.read_text()
instructions = prompt_file.read_text()

prompt = f"""
{instructions}

RTL DESIGN:
{rtl_code}

DESIGN SPECIFICATION:
{specification}
"""

print("===== AssertLLM Sequence Detector Generator =====")
print("RTL loaded!")
print("Specification loaded!")
print("\nGenerating assertions using local LLM...")

raw_response = generate(prompt)
print("\n===== RAW QWEN RESPONSE =====")
print(raw_response)
print("===== END RAW RESPONSE =====\n")
try:
    data = json.loads(raw_response)
    assertions = data["assertions"]

    expected_names = {
        "sequence_1011_detected",
        "detected_matches_state"
    }

    if not isinstance(assertions, list) or len(assertions) != 2:
        raise ValueError("Expected exactly two assertions.")

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

        name = name.strip()
        code = code.strip()

        if name in received_names:
            raise ValueError(f"Duplicate assertion name: {name}")

        if f"property {name};" not in code:
            raise ValueError(f"Property declaration missing: {name}")

        if f"assert property ({name})" not in code:
            raise ValueError(f"Assertion statement missing: {name}")

        received_names.add(name)
        assertion_codes.append(code)

    if received_names != expected_names:
        raise ValueError(
            f"Expected {expected_names}, received {received_names}"
        )

    output_file = (
        PROJECT_DIR / "generated" /
        "sequence_detector_1011_assertions.sv"
    )

    report_file = (
        PROJECT_DIR / "reports" /
        "sequence_detector_1011_llm_response.json"
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
