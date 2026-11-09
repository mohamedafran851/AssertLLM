import csv
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent

RTL_DIR = ROOT / "rtl"
MUTATION_DIR = ROOT / "mutations"
TB = ROOT / "testbench/mux4to1_sva_generated_tb.sv"
BUILD_DIR = ROOT / "obj_mux_mutation"
REPORT = ROOT / "reports/mux4to1_mutation_results.csv"

DESIGNS = [
    ("original", RTL_DIR / "mux4to1.v"),
    ("d0_bug", MUTATION_DIR / "mux4to1_bug_d0.v"),
    ("d1_bug", MUTATION_DIR / "mux4to1_bug_d1.v"),
    ("d2_bug", MUTATION_DIR / "mux4to1_bug_d2.v"),
    ("d3_bug", MUTATION_DIR / "mux4to1_bug_d3.v"),
]


def run_test(name, rtl):
    print(f"\n===== Testing: {name} =====")

    if BUILD_DIR.exists():
        import shutil
        shutil.rmtree(BUILD_DIR)

    compile_cmd = [
        "verilator", "--binary", "--timing", "--assert",
        "-Wall", "-Wno-fatal",
        "-I" + str(ROOT / "generated"),
        "--Mdir", str(BUILD_DIR),
        "--top-module", "mux4to1_sva_generated_tb",
        str(rtl),
        str(TB)
    ]

    compilation = subprocess.run(
        compile_cmd, capture_output=True, text=True
    )

    if compilation.returncode != 0:
        print("COMPILE ERROR")
        print(compilation.stderr)
        return "COMPILE_ERROR", compilation.returncode

    simulation = subprocess.run(
        [str(BUILD_DIR / "Vmux4to1_sva_generated_tb")],
        capture_output=True, text=True
    )

    output = simulation.stdout + simulation.stderr
    print(output)

    if simulation.returncode == 0:
        print("RESULT: PASS")
        return "PASS", 0

    if "Assertion failed" in output:
        print("RESULT: MUTANT DETECTED")
        return "DETECTED", simulation.returncode

    print("RESULT: SIMULATION ERROR")
    return "SIMULATION_ERROR", simulation.returncode


def main():
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    for name, rtl in DESIGNS:
        result, exit_code = run_test(name, rtl)
        rows.append([
            datetime.now().isoformat(timespec="seconds"),
            name,
            rtl.name,
            result,
            exit_code
        ])

    with REPORT.open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "timestamp", "design", "rtl_file", "result", "exit_code"
        ])
        writer.writerows(rows)

    detected = sum(row[3] == "DETECTED" for row in rows)
    passed = sum(row[3] == "PASS" for row in rows)
    errors = sum(row[3] in ("COMPILE_ERROR", "SIMULATION_ERROR") for row in rows)

    print("\n===== MUX MUTATION SUMMARY =====")
    print("Original design passed:", passed == 1)
    print("Mutants detected:", detected, "/ 4")
    print("Errors:", errors)
    print("Detection rate:", f"{detected / 4 * 100:.2f}%")
    print("Report:", REPORT)

    if passed == 1 and detected == 4 and errors == 0:
        print("MUX MUTATION TEST: PASSED")
    else:
        print("MUX MUTATION TEST: NEEDS INVESTIGATION")


if __name__ == "__main__":
    main()
