import csv
import re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "reports"

DESIGNS = {
    "Counter": ("counter", 3),
    "UpDown Counter": ("updown_counter", 3),
    "Controller FSM": ("controller_fsm", 6),
    "4-bit ALU": ("alu4", 7),
    "4:1 MUX": ("mux4to1", 4),
    "Sequence Detector 1011": ("sequence_detector_1011", 2),
}


def analyze_file(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    content = path.read_text()

    properties = re.findall(
        r"\bproperty\s+(\w+)\s*;",
        content
    )

    assertions = re.findall(
        r"\bassert\s+property\s*\(",
        content
    )

    return properties, len(assertions)


def main():
    REPORT_DIR.mkdir(exist_ok=True)

    results = []

    for design, (filename, expected) in DESIGNS.items():
        manual_file = ROOT / "manual" / f"{filename}_assertions.sv"
        generated_file = ROOT / "generated" / f"{filename}_assertions.sv"

        manual_properties, manual_assertions = analyze_file(manual_file)
        llm_properties, llm_assertions = analyze_file(generated_file)

        counts_match = (
            len(manual_properties) == len(llm_properties)
            and manual_assertions == llm_assertions
            and manual_assertions == expected
            and llm_assertions == expected
        )

        results.append({
            "design": design,
            "expected_requirements": expected,
            "manual_properties": len(manual_properties),
            "llm_properties": len(llm_properties),
            "manual_assertions": manual_assertions,
            "llm_assertions": llm_assertions,
            "property_count_match": "YES" if counts_match else "NO",
            "manual_property_names": "; ".join(manual_properties),
            "llm_property_names": "; ".join(llm_properties),
        })

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_path = REPORT_DIR / f"sva_comparison_{timestamp}.csv"
    txt_path = REPORT_DIR / f"sva_comparison_{timestamp}.txt"

    with csv_path.open("w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    total_expected = sum(
        row["expected_requirements"] for row in results
    )
    total_manual = sum(row["manual_assertions"] for row in results)
    total_llm = sum(row["llm_assertions"] for row in results)
    matched_designs = sum(
        row["property_count_match"] == "YES" for row in results
    )

    with txt_path.open("w") as file:
        file.write("MANUAL vs LLM-GENERATED SVA COMPARISON\n")
        file.write("=" * 55 + "\n\n")

        for row in results:
            file.write(f"Design: {row['design']}\n")
            file.write(
                f"Expected requirements: {row['expected_requirements']}\n"
            )
            file.write(
                f"Manual properties/assertions: "
                f"{row['manual_properties']}/{row['manual_assertions']}\n"
            )
            file.write(
                f"LLM properties/assertions: "
                f"{row['llm_properties']}/{row['llm_assertions']}\n"
            )
            file.write(
                f"Property count check: {row['property_count_match']}\n"
            )
            file.write("-" * 55 + "\n")

        file.write("\nSUMMARY\n")
        file.write(f"Designs analyzed: {len(results)}\n")
        file.write(f"Designs with matching counts: {matched_designs}\n")
        file.write(f"Expected requirements: {total_expected}\n")
        file.write(f"Manual assertions: {total_manual}\n")
        file.write(f"LLM assertions: {total_llm}\n")
        file.write(
            "\nNOTE: Matching property/assertion counts do not prove "
            "semantic equivalence or functional correctness.\n"
        )
        file.write(
            "Requirement-level matches must be supported by manual "
            "review and simulation.\n"
        )

    print("\nMANUAL vs LLM SVA COMPARISON")
    print("=" * 45)

    for row in results:
        print(
            f"{row['design']:<25} "
            f"Manual: {row['manual_assertions']} | "
            f"LLM: {row['llm_assertions']} | "
            f"Count match: {row['property_count_match']}"
        )

    print("=" * 45)
    print(f"Expected requirements: {total_expected}")
    print(f"Manual assertions:     {total_manual}")
    print(f"LLM assertions:        {total_llm}")
    print(f"Matching designs:      {matched_designs}/{len(results)}")
    print("\nReports saved:")
    print(csv_path)
    print(txt_path)


if __name__ == "__main__":
    main()
