import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"

DESIGNS = {
    "Counter": {
        "manual": "manual_counter_mutation_results.csv",
        "llm": "mutation_results.csv",
        "expected": 3,
    },
    "UpDown Counter": {
        "manual": "manual_updown_mutation_results.csv",
        "llm": "updown_mutation_results.csv",
        "expected": 3,
    },
    "Controller FSM": {
        "manual": "manual_fsm_mutation_results.csv",
        "llm": "fsm_mutation_results.csv",
        "expected": 4,
    },
    "4-bit ALU": {
        "manual": "manual_remaining_mutation_20261109_115639.csv",
        "manual_key": "alu4",
        "llm": "alu4_mutation_results.csv",
        "expected": 7,
    },
    "4:1 MUX": {
        "manual": "manual_remaining_mutation_20261109_115639.csv",
        "manual_key": "mux4to1",
        "llm": "mux4to1_mutation_results.csv",
        "expected": 4,
    },
    "Sequence Detector 1011": {
        "manual": "manual_remaining_mutation_20261109_115639.csv",
        "manual_key": "sequence_detector_1011",
        "llm": "sequence_detector_1011_mutation_results.csv",
        "expected": 2,
    },
}


def read_rows(filename):
    path = REPORTS / filename
    with path.open(newline="") as file:
        return list(csv.DictReader(file))


def normalize(value):
    return str(value or "").strip().upper()


def latest_per_test(rows):
    """Keep the last recorded result for each test/mutant."""
    result = {}
    for row in rows:
        test = (
            row.get("design")
            or row.get("Test")
            or row.get("Design")
            or ""
        ).strip()
        if test:
            result[test] = row
    return result


def get_results(filename, design_name):
    rows = read_rows(filename)

    # The combined manual report stores multiple designs in one CSV.
    if "Test" in rows[0] and "Result" in rows[0]:
        rows = [
            row for row in rows
            if row.get("Design", "").strip() == design_name
        ]
        tests = {
            row["Test"].strip(): normalize(row["Result"])
            for row in rows
        }
    else:
        tests = {
            name: normalize(row.get("result") or row.get("Detected") or row.get("Status"))
            for name, row in latest_per_test(rows).items()
        }

    original = tests.get("original", "")
    mutants = {
        name: status
        for name, status in tests.items()
        if name.lower() != "original"
    }

    detected = sum(
        status in {"DETECTED", "BUG_DETECTED", "YES"}
        for status in mutants.values()
    )

    return original, detected, len(mutants)


def main():
    results = []

    for design, config in DESIGNS.items():
        manual_original, manual_detected, manual_total = get_results(
            config["manual"], config.get("manual_key", design)
        )
        llm_original, llm_detected, llm_total = get_results(
            config["llm"], design
        )

        expected = config["expected"]

        results.append({
            "Design": design,
            "Manual Original": manual_original,
            "Manual Detected": manual_detected,
            "Manual Mutants": manual_total,
            "Manual Rate": f"{manual_detected / expected * 100:.1f}%",
            "LLM Original": llm_original,
            "LLM Detected": llm_detected,
            "LLM Mutants": llm_total,
            "LLM Rate": f"{llm_detected / expected * 100:.1f}%",
        })

    csv_path = REPORTS / "final_manual_vs_llm_comparison.csv"
    txt_path = REPORTS / "final_manual_vs_llm_comparison.txt"

    fields = list(results[0].keys())
    with csv_path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    total_expected = sum(item["expected"] for item in DESIGNS.values())
    manual_total = sum(item["Manual Detected"] for item in results)
    llm_total = sum(item["LLM Detected"] for item in results)

    lines = [
        "ASSERTLLM - FINAL MANUAL VS LLM-GENERATED SVA COMPARISON",
        "=" * 62,
        "",
        "DESIGN-WISE MUTATION RESULTS",
        "-" * 62,
    ]

    for item in results:
        lines.extend([
            item["Design"],
            f"  Manual SVA: {item['Manual Detected']}/{item['Manual Mutants']} mutants detected",
            f"  LLM SVA:    {item['LLM Detected']}/{item['LLM Mutants']} mutants detected",
            "",
        ])

    lines.extend([
        "OVERALL RESULTS",
        "-" * 62,
        f"Selected mutants: {total_expected}",
        f"Manual SVA detected: {manual_total}/{total_expected} "
        f"({manual_total / total_expected * 100:.1f}%)",
        f"LLM SVA detected: {llm_total}/{total_expected} "
        f"({llm_total / total_expected * 100:.1f}%)",
        "",
        "EXPERIMENTAL LIMITATIONS",
        "-" * 62,
        "1. Results apply only to the selected mutants in this experiment.",
        "2. Equal mutation scores do not prove semantic equivalence.",
        "3. Requirement matching was based on manual review, not formal proof.",
        "4. Simulation-based mutation testing is not formal verification.",
        "5. Clocked assertions for combinational ALU and MUX designs sample",
        "   outputs at clock edges rather than continuously.",
        "6. Identical testbench stimulus has not yet been verified for every",
        "   manual/generated pair, particularly Counter, UpDown Counter,",
        "   and Controller FSM.",
        "",
        "CONCLUSION",
        "-" * 62,
        "The experiment compares manually written and LLM-generated SVA",
        "using the selected RTL mutations across six designs. The results",
        "should be interpreted within the stated experimental limitations.",
    ])

    txt_path.write_text("\n".join(lines) + "\n")

    print("Comparison reports created:")
    print(csv_path)
    print(txt_path)
    print()
    print(f"Manual detection: {manual_total}/{total_expected}")
    print(f"LLM detection:    {llm_total}/{total_expected}")


if __name__ == "__main__":
    main()
