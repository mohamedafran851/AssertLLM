
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REPORTS = [
    ROOT / "reports/mutation_results.csv",
    ROOT / "reports/updown_mutation_results.csv",
    ROOT / "reports/fsm_mutation_results.csv",
    ROOT / "reports/alu4_mutation_results.csv",
    ROOT / "reports/mux4to1_mutation_results.csv",
    ROOT / "reports/sequence_detector_1011_mutation_results.csv",
]

EXPECTED_ORIGINALS = {
    "rtl/counter.v",
    "rtl/updown_counter.v",
    "rtl/controller_fsm.v",
    "rtl/alu4.v",
    "rtl/mux4to1.v",
    "rtl/sequence_detector_1011.v",
}

EXPECTED_MUTANTS = {
    "mutations/counter_bug_increment.v",
    "mutations/counter_bug_no_reset.v",
    "mutations/counter_bug_reset_value.v",

    "mutations/updown_bug_increment.v",
    "mutations/updown_bug_decrement.v",
    "mutations/updown_bug_direction.v",

    "mutations/controller_fsm_bug_start.v",
    "mutations/controller_fsm_bug_finish.v",
    "mutations/controller_fsm_bug_done.v",
    "mutations/controller_fsm_bug_outputs.v",

    "mutations/alu4_bug_add.v",
    "mutations/alu4_bug_sub.v",
    "mutations/alu4_bug_and.v",
    "mutations/alu4_bug_or.v",
    "mutations/alu4_bug_xor.v",
    "mutations/alu4_bug_not.v",
    "mutations/alu4_bug_invalid.v",

    "mutations/mux4to1_bug_d0.v",
    "mutations/mux4to1_bug_d1.v",
    "mutations/mux4to1_bug_d2.v",
    "mutations/mux4to1_bug_d3.v",

    "mutations/sequence_detector_1011_bug_transition.v",
    "mutations/sequence_detector_1011_bug_output.v",
}

def normalize_result(value):
    value = value.strip().upper()
    value = value.replace(" ", "_")
    return value


def load_latest_results():
    originals = {}
    mutants = {}

    sequence_mutants = {
        "bug_transition": "mutations/sequence_detector_1011_bug_transition.v",
        "bug_output": "mutations/sequence_detector_1011_bug_output.v",
    }

    for report in REPORTS:
        if not report.exists():
            print(f"WARNING: Missing report: {report.name}")
            continue

        with open(report, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            # Special format used by the sequence detector report.
            if report.name == "sequence_detector_1011_mutation_results.csv":
                required = {"Design", "Status"}

                if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                    print(f"ERROR: Invalid sequence detector CSV: {report.name}")
                    continue

                for row in reader:
                    design = row["Design"].strip().lower()
                    result = normalize_result(row["Status"])

                    if design == "original":
                        originals["rtl/sequence_detector_1011.v"] = result
                    elif design in sequence_mutants:
                        if result == "BUG_DETECTED":
                            result = "DETECTED"
                        mutants[sequence_mutants[design]] = result

                continue

            required_columns = {"design", "rtl_file", "result"}

            if not reader.fieldnames or not required_columns.issubset(set(reader.fieldnames)):
                print(f"ERROR: Invalid CSV format: {report.name}")
                continue

            for row in reader:
                design = row["design"].strip().lower()
                rtl_file = row["rtl_file"].strip()
                result = normalize_result(row["result"])

                # MUX report stores filenames without their directory.
                if report.name == "mux4to1_mutation_results.csv":
                    if design == "original":
                        rtl_file = "rtl/" + Path(rtl_file).name
                    else:
                        rtl_file = "mutations/" + Path(rtl_file).name

                if design == "original":
                    originals[rtl_file] = result
                else:
                    mutants[rtl_file] = result

    return originals, mutants


def main():
    print("===== ASSERTLLM RELIABLE COMBINED EVALUATION =====")

    originals, mutants = load_latest_results()

    print("\nORIGINAL RTL RESULTS")

    for rtl_file in sorted(EXPECTED_ORIGINALS):
        result = originals.get(rtl_file, "MISSING")
        print(f"{rtl_file:50} : {result}")

    print("\nUNIQUE MUTANT RESULTS")

    for rtl_file in sorted(EXPECTED_MUTANTS):
        result = mutants.get(rtl_file, "MISSING")
        print(f"{rtl_file:55} : {result}")

    original_passed = sum(
        originals.get(path) == "PASS"
        for path in EXPECTED_ORIGINALS
    )

    detected = sum(
        mutants.get(path) == "DETECTED"
        for path in EXPECTED_MUTANTS
    )

    not_detected = sum(
        mutants.get(path) == "NOT_DETECTED"
        for path in EXPECTED_MUTANTS
    )

    compile_errors = sum(
        mutants.get(path) == "COMPILE_ERROR"
        for path in EXPECTED_MUTANTS
    )

    simulation_errors = sum(
        mutants.get(path) == "SIMULATION_ERROR"
        for path in EXPECTED_MUTANTS
    )

    other = len(EXPECTED_MUTANTS) - (
        detected + not_detected + compile_errors + simulation_errors
    )

    missing_originals = len(EXPECTED_ORIGINALS) - len(
        EXPECTED_ORIGINALS.intersection(originals)
    )

    missing_mutants = len(EXPECTED_MUTANTS) - len(
        EXPECTED_MUTANTS.intersection(mutants)
    )

    total = len(EXPECTED_MUTANTS)
    detection_rate = detected / total * 100 if total else 0

    print("\n========== SUMMARY ==========")
    print(f"Expected original designs : {len(EXPECTED_ORIGINALS)}")
    print(f"Original designs passed   : {original_passed}")
    print(f"Missing original results  : {missing_originals}")
    print(f"Expected unique mutants   : {total}")
    print(f"Detected                  : {detected}")
    print(f"Not detected              : {not_detected}")
    print(f"Compile errors            : {compile_errors}")
    print(f"Simulation errors         : {simulation_errors}")
    print(f"Other/missing results     : {other}")
    print(f"Unique detection rate     : {detection_rate:.2f}%")

    all_originals_pass = (
        original_passed == len(EXPECTED_ORIGINALS)
        and missing_originals == 0
    )

    all_mutants_valid = (
        detected + not_detected == total
        and missing_mutants == 0
    )

    if all_originals_pass and all_mutants_valid:
        print("\nCOMBINED EVALUATION: PASSED")
        print("All original designs passed.")
        print("All expected mutants have valid results.")
        return 0

    print("\nCOMBINED EVALUATION: FAILED")
    print("Investigate missing results, original failures,")
    print("compile errors, simulation errors, or other results.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
