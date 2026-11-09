
from pathlib import Path
import subprocess
import csv
from datetime import datetime
import shutil

PROJECT_DIR = Path(__file__).resolve().parent.parent

RTL_DIR = PROJECT_DIR / "rtl"
TB_FILE = PROJECT_DIR / "testbench" / "controller_fsm_sva_manual_tb.sv"
REPORT_FILE = PROJECT_DIR / "reports" / "manual_fsm_mutation_results.csv"

DESIGNS = [
    ("original", RTL_DIR / "controller_fsm.v"),
    ("start_bug", PROJECT_DIR / "mutations" / "controller_fsm_bug_start.v"),
    ("finish_bug", PROJECT_DIR / "mutations" / "controller_fsm_bug_finish.v"),
    ("done_bug", PROJECT_DIR / "mutations" / "controller_fsm_bug_done.v"),
    ("outputs_bug", PROJECT_DIR / "mutations" / "controller_fsm_bug_outputs.v"),
]


def run_design(name, rtl_file):

    print(f"\n===== TESTING MANUAL {name.upper()} =====")

    build_dir = PROJECT_DIR / f"obj_manual_fsm_mutation_{name}"

    if build_dir.exists():
        shutil.rmtree(build_dir)

    compile_command = [
        "verilator",
        "--binary",
        "--timing",
        "--assert",
        "-Wall",
        "-Wno-fatal",
        "-Imanual",
        "--Mdir",
        str(build_dir),
        "--top-module",
        "controller_fsm_sva_manual_tb",
        str(rtl_file),
        str(TB_FILE),
    ]

    try:
        compilation = subprocess.run(
            compile_command,
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
    except (OSError, subprocess.SubprocessError) as error:
        print(f"COMPILATION TOOL ERROR: {error}")
        return "COMPILE_ERROR", -1

    if compilation.returncode != 0:
        print("RESULT: COMPILE_ERROR")
        print(compilation.stdout)
        print(compilation.stderr)
        return "COMPILE_ERROR", compilation.returncode

    print("Compilation successful.")

    executable = build_dir / "Vcontroller_fsm_sva_manual_tb"

    if not executable.exists():
        print("RESULT: SIMULATION_ERROR")
        print("Simulation executable was not created.")
        return "SIMULATION_ERROR", -1

    try:
        simulation = subprocess.run(
            [str(executable)],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
    except (OSError, subprocess.SubprocessError) as error:
        print(f"SIMULATION TOOL ERROR: {error}")
        return "SIMULATION_ERROR", -1

    output = simulation.stdout + simulation.stderr
    print(output)

    if name == "original":

        if simulation.returncode == 0:
            print("RESULT: ORIGINAL PASSED")
            return "PASS", 0

        print("RESULT: ORIGINAL FAILED")
        return "ORIGINAL_FAILED", simulation.returncode

    assertion_failed = "Assertion failed" in output

    if simulation.returncode != 0 and assertion_failed:
        print("RESULT: MUTANT DETECTED")
        return "DETECTED", simulation.returncode

    if simulation.returncode == 0:
        print("RESULT: MUTANT NOT DETECTED")
        return "NOT_DETECTED", 0

    print("RESULT: SIMULATION ERROR")
    return "SIMULATION_ERROR", simulation.returncode


def main():

    print("===== ASSERTLLM MANUAL FSM MUTATION TEST =====")

    results = []
    infrastructure_failure = False

    for name, rtl_file in DESIGNS:

        if not rtl_file.exists():
            raise FileNotFoundError(f"Missing RTL file: {rtl_file}")

        result, exit_code = run_design(name, rtl_file)

        results.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "design": name,
            "rtl_file": str(rtl_file.relative_to(PROJECT_DIR)),
            "result": result,
            "exit_code": exit_code
        })

        if result in (
            "COMPILE_ERROR",
            "SIMULATION_ERROR",
            "ORIGINAL_FAILED"
        ):
            infrastructure_failure = True

        if name == "original" and result != "PASS":
            print("\nOriginal FSM failed. Stopping mutation testing.")
            break

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "timestamp",
        "design",
        "rtl_file",
        "result",
        "exit_code"
    ]

    file_exists = REPORT_FILE.exists()

    with REPORT_FILE.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerows(results)

    print("\n===== MANUAL FSM MUTATION SUMMARY =====")

    for item in results:
        print(f"{item['design']}: {item['result']}")

    mutant_results = [
        item for item in results
        if item["design"] != "original"
    ]

    total = len(mutant_results)
    detected = sum(
        item["result"] == "DETECTED"
        for item in mutant_results
    )

    valid = sum(
        item["result"] in ("DETECTED", "NOT_DETECTED")
        for item in mutant_results
    )

    print(f"\nMutants tested: {total}")
    print(f"Valid mutant results: {valid}")
    print(f"Mutants detected: {detected}")

    if valid:
        print(f"Detection rate: {detected / valid * 100:.2f}%")
    else:
        print("Detection rate: Cannot calculate")

    print("\nResults saved to:", REPORT_FILE)

    if infrastructure_failure:
        print("\nMANUAL FSM MUTATION TEST: INFRASTRUCTURE FAILURE")
        return 1

    print("\nMANUAL FSM MUTATION TEST: COMPLETED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
