from pathlib import Path
import subprocess
import csv

PROJECT_DIR = Path(__file__).resolve().parent.parent

RTL_DIR = PROJECT_DIR / "rtl"
MUTATION_DIR = PROJECT_DIR / "mutations"
TB_DIR = PROJECT_DIR / "testbench"
BUILD_DIR = PROJECT_DIR / "obj_seq_mutation"
REPORT_DIR = PROJECT_DIR / "reports"

TESTBENCH = TB_DIR / "sequence_detector_1011_sva_generated_tb.sv"

DESIGNS = [
    ("original", RTL_DIR / "sequence_detector_1011.v"),
    ("bug_transition", MUTATION_DIR / "sequence_detector_1011_bug_transition.v"),
    ("bug_output", MUTATION_DIR / "sequence_detector_1011_bug_output.v"),
]

results = []

print("===== SEQUENCE DETECTOR MUTATION TEST =====")

for name, rtl_file in DESIGNS:
    print(f"\n===== Testing: {name} =====")

    if BUILD_DIR.exists():
        subprocess.run(["rm", "-rf", str(BUILD_DIR)])

    compile_command = [
        "verilator",
        "--binary",
        "--timing",
        "--assert",
        "-Wall",
        "-Wno-fatal",
        "-I" + str(PROJECT_DIR / "generated"),
        "--Mdir",
        str(BUILD_DIR),
        "--top-module",
        "sequence_detector_1011_sva_generated_tb",
        str(rtl_file),
        str(TESTBENCH),
    ]

    compile_result = subprocess.run(
        compile_command,
        capture_output=True,
        text=True
    )

    if compile_result.returncode != 0:
        print("COMPILATION ERROR")
        print(compile_result.stderr)
        results.append([name, "COMPILE_ERROR", "NO"])
        continue

    executable = (
        BUILD_DIR / "Vsequence_detector_1011_sva_generated_tb"
    )

    simulation = subprocess.run(
        [str(executable)],
        capture_output=True,
        text=True
    )

    output = simulation.stdout + simulation.stderr

    if name == "original":
        status = (
            "PASS"
            if simulation.returncode == 0
            and "GENERATED SVA TEST: PASSED" in output
            else "FAIL"
        )
        detected = "N/A"

    else:
        assertion_failed = (
            simulation.returncode != 0
            and (
                "Assertion failed" in output
                or "%Error" in output
            )
        )

        status = "BUG_DETECTED" if assertion_failed else "BUG_MISSED"
        detected = "YES" if assertion_failed else "NO"

    print(output)
    print("RESULT:", status)

    results.append([name, status, detected])

REPORT_DIR.mkdir(exist_ok=True)

report_file = REPORT_DIR / "sequence_detector_1011_mutation_results.csv"

with report_file.open("w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Design", "Status", "Detected"])
    writer.writerows(results)

original_pass = results[0][1] == "PASS"
mutants = results[1:]
detected_count = sum(row[2] == "YES" for row in mutants)
total_mutants = len(mutants)
errors = sum(row[1] == "COMPILE_ERROR" for row in results)

rate = (
    detected_count / total_mutants * 100
    if total_mutants else 0
)

print("\n===== FINAL MUTATION SUMMARY =====")
print("Original design passed:", original_pass)
print(f"Mutants detected: {detected_count}/{total_mutants}")
print(f"Detection rate: {rate:.2f}%")
print("Compilation errors:", errors)
print("Report:", report_file)

if original_pass and detected_count == total_mutants and errors == 0:
    print("\nSEQUENCE DETECTOR MUTATION TEST: PASSED")
else:
    print("\nSEQUENCE DETECTOR MUTATION TEST: NEEDS REVIEW")
