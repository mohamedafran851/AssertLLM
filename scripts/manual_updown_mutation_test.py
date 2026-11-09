
import subprocess
import shutil
import csv
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BUILD_ROOT = ROOT / "obj_manual_updown_mutations"
REPORT_FILE = ROOT / "reports/manual_updown_mutation_results.csv"

TESTBENCH = ROOT / "testbench/updown_counter_sva_manual_tb.sv"

DESIGNS = {
    "original": ROOT / "rtl/updown_counter.v",
    "increment_bug": ROOT / "mutations/updown_bug_increment.v",
    "decrement_bug": ROOT / "mutations/updown_bug_decrement.v",
    "direction_bug": ROOT / "mutations/updown_bug_direction.v",
}

MUTANTS = [
    "increment_bug",
    "decrement_bug",
    "direction_bug"
]


def test_design(name, rtl_file):
    print(f"\n===== Testing: {name} =====")

    build_dir = BUILD_ROOT / name

    if build_dir.exists():
        shutil.rmtree(build_dir)

    build_dir.mkdir(parents=True, exist_ok=True)

    command = [
        "verilator",
        "--binary",
        "--timing",
        "--assert",
        "-Wall",
        "-Wno-fatal",
        "-Imanual",
        "--Mdir", str(build_dir),
        "--top-module", "updown_counter_sva_manual_tb",
        str(rtl_file),
        str(TESTBENCH),
    ]

    try:
        compile_result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True
        )
    except (OSError, subprocess.SubprocessError) as error:
        print(f"COMPILATION TOOL ERROR: {error}")
        return "COMPILE_ERROR"

    if compile_result.returncode != 0:
        print("RESULT: COMPILE_ERROR")
        print(compile_result.stdout)
        print(compile_result.stderr)
        return "COMPILE_ERROR"

    print("Compilation successful.")

    executable = build_dir / "Vupdown_counter_sva_manual_tb"

    if not executable.exists():
        print("RESULT: SIMULATION_ERROR")
        print("Simulation executable was not created.")
        return "SIMULATION_ERROR"

    try:
        simulation = subprocess.run(
            [str(executable)],
            cwd=ROOT,
            capture_output=True,
            text=True
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
            rtl_file = DESIGNS[name].relative_to(ROOT)

            writer.writerow([
                timestamp,
                name,
                str(rtl_file),
                result
            ])

    print(f"\nResults saved to: {REPORT_FILE}")


def main():
    print("===== ASSERTLLM MANUAL UP/DOWN MUTATION TEST =====")

    results = {}

    for name, rtl_file in DESIGNS.items():
        results[name] = test_design(name, rtl_file)

    print("\n========== FINAL MANUAL RESULTS ==========")

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
        print("\nMANUAL UP/DOWN MUTATION TEST: PASSED")
    else:
        print("\nMANUAL UP/DOWN MUTATION TEST: NEEDS INVESTIGATION")


if __name__ == "__main__":
    main()
