import json
from pathlib import Path
from llm_client import generate

PROJECT_DIR = Path(__file__).resolve().parent.parent

PROMPT_FILE = PROJECT_DIR / "prompts/mux4to1_llm_prompt.txt"
OUTPUT_FILE = PROJECT_DIR / "generated/mux4to1_assertions.sv"
REPORT_FILE = PROJECT_DIR / "reports/mux4to1_llm_response.json"

EXPECTED_NAMES = [
    "mux_sel_00_property",
    "mux_sel_01_property",
    "mux_sel_10_property",
    "mux_sel_11_property"
]


def main():
    prompt = PROMPT_FILE.read_text()

    print("===== MUX4TO1 LLM ASSERTION GENERATOR =====")

    response = generate(prompt)
    data = json.loads(response)
    assertions = data["assertions"]

    if len(assertions) != 4:
        raise ValueError("Expected exactly four assertions")

    actual_names = [item["name"] for item in assertions]

    if actual_names != EXPECTED_NAMES:
        raise ValueError("Incorrect assertion names or order")

    generated_code = ""

    for item in assertions:
        code = item["code"].strip()

        if "assert property" not in code:
            code += f"\nassert property ({item['name']});"

        generated_code += code + "\n\n"

    OUTPUT_FILE.write_text(generated_code)
    REPORT_FILE.write_text(json.dumps(data, indent=4))

    print("Assertions generated:", len(assertions))
    print("Output:", OUTPUT_FILE)
    print("Report:", REPORT_FILE)


if __name__ == "__main__":
    main()
