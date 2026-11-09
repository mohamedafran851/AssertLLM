
from pathlib import Path
import subprocess
import shutil
import csv
from datetime import datetime

PROJECT_DIR = Path(__file__).resolve().parent.parent

TESTBENCH = PROJECT_DIR / "testbench/counter_sva_manual_tb.sv"
REPORT_FILE = PROJECT_DIR / "reports/manual_counter_mutation_results.csv"

DESIGNS = {
    "original": PROJECT_DIR / "rtl/counter.v",
    "increment_bug": PROJECT_DIR / "mutations/counter_bug_increment.v",
    "no_reset_bug": PROJECT_DIR / "mutations/counter_bug_no_reset.v",
    "reset_value_bug": PROJECT_DIR / "mutations/counter_bug_reset_value.v",
}

MUTANTS = [
    "increment_bug",
    "no_reset_bug",
    "reset_value_bug"
]


def test_design(name, rtl_file):
    print(f"\n===== Testing: {name} =====")

    build_dir = PROJECT_DIR / f"obj_manual_counter_{name}"

    if build_dir.exists():
        shutil.rmtree(build_dir)

    build_dir.mkdir(parents=True, exist_ok=True)

    compile_command = [
        "verilator",
        "--binary",
        "--timing",
        "--assert",
        "-Wall",
        "-Wno-fatal",
        "-Imanual",
        "--Mdir", str(build_dir),
        "--top-module", "counter_sva_manual_tb",
        str(rtl_file),
        str(TESTBENCH),
    ]

    try:
        compilation = subprocess.run(
            compile_command,
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )
    except (OSError, subprocess.SubprocessError) as error:
        print(f"COMPILATION TOOL ERROR: {error}")
        return "COMPILE_ERROR"

    if compilation.returncode != 0:
        print("RESULT: COMPILE_ERROR")
        print(compilation.stdout)
        print(compilation.stderr)
        return "COMPILE_ERROR"

    print("Compilation successful.")

    executable = build_dir / "Vcounter_sva_manual_tb"

    if not executable.exists():
        print("RESULT: SIMULATION_ERROR")
        print("Simulation executable was not created.")
        return "SIMULATION_ERROR"

    try:
        simulation = subprocess.run(
            [str(executable)],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )
    except (OSError, subprocess.SubprocessError) as error:
        print(f"SIMULATION TOOL ERROR: {error}")
        return "SIMULATION_ERROR"

    output = simulation.stdout + simulation.stderr
    print(output)

    assertion_failed = "Assertion failed" in output

    if name == "original":
        if simulation.returncode == 0:
            print("RESULT: ORIGINAL PASS")
            return "PASS"

        print("RESULT: ORIGINAL_FAILED")
        return "ORIGINAL_FAILED"

    if simulation.returncode != 0 and assertion_failed:
        print("RESULT: BUG DETECTED")
        return "DETECTED"

    if simulation.returncode == 0:
        print("RESULT: BUG NOT DETECTED")
        return "NOT_DETECTED"

    print("RESULT: SIMULATION_ERROR")
    return "SIMULATION_ERROR"


def save_results(results):
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    file_exists = (
        REPORT_FILE.exists()
        and REPORT_FILE.stat().st_size > 0
    )

    timestamp = datetime.now().isoformat(timespec="seconds")

    with open(REPORT_FILE, "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "design",
                "rtl_file",
                "result"
            ])

        for name, result in results.items():
            rtl_file = DESIGNS[name].relative_to(PROJECT_DIR)

            writer.writerow([
                timestamp,
                name,
                str(rtl_file),
                result
            ])

    print(f"\nResults saved to: {REPORT_FILE}")


def main():
    results = {}

    print("===== ASSERTLLM MANUAL COUNTER MUTATION TEST =====")

    for name, rtl_file in DESIGNS.items():
        results[name] = test_design(name, rtl_file)

    print("\n========== FINAL MANUAL MUTATION REPORT ==========")

    for name, result in results.items():
        print(f"{name:20} : {result}")

    detected = sum(
        results[name] == "DETECTED"
        for name in MUTANTS
    )

    valid_mutants = sum(
        results[name] in ("DETECTED", "NOT_DETECTED")
        for name in MUTANTS
    )

    print(f"\nMutants tested: {len(MUTANTS)}")
    print(f"Valid mutant results: {valid_mutants}")
    print(f"Mutants detected: {detected}")

    if valid_mutants:
        rate = detected / valid_mutants * 100
        print(f"Mutation detection rate: {rate:.2f}%")
    else:
        print("Mutation detection rate: Cannot calculate")

    save_results(results)

    if (
        results["original"] == "PASS"
        and detected == len(MUTANTS)
    ):
        print("\nMANUAL COUNTER MUTATION TEST: PASSED")
    else:
        print("\nMANUAL COUNTER MUTATION TEST: NEEDS INVESTIGATION")


if __name__ == "__main__":
    main()
