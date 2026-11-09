from pathlib import Path
import subprocess
import shutil

PROJECT_DIR = Path(__file__).resolve().parent.parent

RTL = PROJECT_DIR / "rtl" / "counter.v"
BUGGY_RTL = PROJECT_DIR / "mutations" / "counter_bug.v"
TESTBENCH = PROJECT_DIR / "testbench" / "counter_sva_tb.sv"


def run_command(command):
    return subprocess.run(
        command,
        capture_output=True,
        text=True
    )


def test_design(name, rtl_file, expected_pass):

    print(f"\n===== Testing {name} =====")

    build_dir = PROJECT_DIR / f"obj_{name}"

    if build_dir.exists():
        shutil.rmtree(build_dir)

    compile_command = [
        "verilator",
        "--binary",
        "--timing",
        "--assert",
        "-Wall",
        "-Wno-fatal",
        "--Mdir", str(build_dir),
        "--top-module", "counter_sva_tb",
        str(rtl_file),
        str(TESTBENCH)
    ]

    compilation = run_command(compile_command)

    if compilation.returncode != 0:
        print("COMPILATION FAILED")
        print(compilation.stdout)
        print(compilation.stderr)
        return False

    executable = build_dir / "Vcounter_sva_tb"

    simulation = run_command([str(executable)])

    output = simulation.stdout + simulation.stderr

    print(output)

    if expected_pass:
        passed = (
            simulation.returncode == 0
            and "TEST COMPLETED" in output
            and "Assertion failed" not in output
        )
    else:
        passed = (
            simulation.returncode != 0
            and "INCREMENT ASSERTION FAILED" in output
        )

    print("RESULT:", "PASS" if passed else "UNEXPECTED RESULT")

    return passed


print("===== AssertLLM Mutation Testing =====")

original_result = test_design(
    "original",
    RTL,
    expected_pass=True
)

mutant_result = test_design(
    "mutant",
    BUGGY_RTL,
    expected_pass=False
)

print("\n===== FINAL REPORT =====")

print("Original RTL:", "PASS" if original_result else "FAIL")
print("Mutated RTL:", "DETECTED" if mutant_result else "NOT DETECTED")

if original_result and mutant_result:
    print("\nASSERTLLM MUTATION TEST PASSED")
else:
    print("\nASSERTLLM MUTATION TEST FAILED")
