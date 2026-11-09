from pathlib import Path
import subprocess
import shutil
import csv
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent

DESIGNS = {
    "alu4": {
        "tb": "alu4_sva_manual_tb",
        "testbench": ROOT / "testbench/alu4_sva_manual_tb.sv",
        "rtl": ROOT / "rtl/alu4.v",
        "mutants": [
            ("add_bug", ROOT / "mutations/alu4_bug_add.v"),
            ("sub_bug", ROOT / "mutations/alu4_bug_sub.v"),
            ("and_bug", ROOT / "mutations/alu4_bug_and.v"),
            ("or_bug", ROOT / "mutations/alu4_bug_or.v"),
            ("xor_bug", ROOT / "mutations/alu4_bug_xor.v"),
            ("not_bug", ROOT / "mutations/alu4_bug_not.v"),
            ("invalid_bug", ROOT / "mutations/alu4_bug_invalid.v"),
        ],
    },
    "mux4to1": {
        "tb": "mux4to1_sva_manual_tb",
        "testbench": ROOT / "testbench/mux4to1_sva_manual_tb.sv",
        "rtl": ROOT / "rtl/mux4to1.v",
        "mutants": [
            ("d0_bug", ROOT / "mutations/mux4to1_bug_d0.v"),
            ("d1_bug", ROOT / "mutations/mux4to1_bug_d1.v"),
            ("d2_bug", ROOT / "mutations/mux4to1_bug_d2.v"),
            ("d3_bug", ROOT / "mutations/mux4to1_bug_d3.v"),
        ],
    },
    "sequence_detector_1011": {
        "tb": "sequence_detector_1011_sva_manual_tb",
        "testbench": ROOT / "testbench/sequence_detector_1011_sva_manual_tb.sv",
        "rtl": ROOT / "rtl/sequence_detector_1011.v",
        "mutants": [
            ("bug_transition", ROOT / "mutations/sequence_detector_1011_bug_transition.v"),
            ("bug_output", ROOT / "mutations/sequence_detector_1011_bug_output.v"),
        ],
    },
}

def run_test(design, config, name, rtl_file):
    print(f"\n===== {design.upper()} : {name.upper()} =====")

    build_dir = ROOT / f"obj_manual_remaining_{design}_{name}"

    if build_dir.exists():
        shutil.rmtree(build_dir)

    command = [
        "verilator",
        "--binary",
        "--timing",
        "--assert",
        "-Wall",
        "-Wno-fatal",
        "-Imanual",
        "--Mdir", str(build_dir),
        "--top-module", config["tb"],
        str(rtl_file),
        str(config["testbench"]),
    ]

    compilation = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True
    )

    if compilation.returncode != 0:
        print("RESULT: COMPILE_ERROR")
        print(compilation.stderr)
        return "COMPILE_ERROR"

    executable = build_dir / f"V{config['tb']}"

    simulation = subprocess.run(
        [str(executable)], cwd=ROOT, capture_output=True, text=True
    )

    output = simulation.stdout + simulation.stderr
    print(output)

    if name == "original":
        if simulation.returncode == 0:
            print("RESULT: ORIGINAL PASS")
            return "PASS"
        print("RESULT: ORIGINAL FAILED")
        return "ORIGINAL_FAILED"

    if simulation.returncode != 0 and "Assertion failed" in output:
        print("RESULT: MUTANT DETECTED")
        return "DETECTED"

    if simulation.returncode == 0:
        print("RESULT: MUTANT NOT DETECTED")
        return "NOT_DETECTED"

    print("RESULT: SIMULATION ERROR")
    return "SIMULATION_ERROR"


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_csv = ROOT / "reports" / f"manual_remaining_mutation_{timestamp}.csv"
    report_txt = ROOT / "reports" / f"manual_remaining_mutation_{timestamp}.txt"

    rows = []

    for design, config in DESIGNS.items():
        original_result = run_test(
            design, config, "original", config["rtl"]
        )
        rows.append([design, "original", original_result])

        for name, rtl_file in config["mutants"]:
            result = run_test(design, config, name, rtl_file)
            rows.append([design, name, result])

    with report_csv.open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Design", "Test", "Result"])
        writer.writerows(rows)

    originals = [r for r in rows if r[1] == "original"]
    mutants = [r for r in rows if r[1] != "original"]

    detected = sum(r[2] == "DETECTED" for r in mutants)
    not_detected = sum(r[2] == "NOT_DETECTED" for r in mutants)
    errors = sum(r[2] in ("COMPILE_ERROR", "SIMULATION_ERROR") for r in rows)
    original_pass = sum(r[2] == "PASS" for r in originals)

    summary = [
        "ASSERTLLM - MANUAL SVA MUTATION EVALUATION",
        "=" * 48,
        f"Original designs passed: {original_pass}/{len(originals)}",
        f"Mutants tested: {len(mutants)}",
        f"Mutants detected: {detected}",
        f"Mutants not detected: {not_detected}",
        f"Compile/simulation errors: {errors}",
        f"Mutation detection rate: {detected / len(mutants) * 100:.2f}%",
        "",
        "Design-wise results:",
    ]

    for design in DESIGNS:
        design_rows = [r for r in mutants if r[0] == design]
        design_detected = sum(r[2] == "DETECTED" for r in design_rows)
        summary.append(
            f"{design}: {design_detected}/{len(design_rows)} mutants detected"
        )

    summary += [
        "",
        "Note: This score applies only to the selected mutants and testbenches.",
        "=" * 48,
    ]

    report_txt.write_text("\n".join(summary) + "\n")

    print("\n".join(summary))
    print(f"\nCSV report: {report_csv}")
    print(f"TXT report: {report_txt}")


if __name__ == "__main__":
    main()
