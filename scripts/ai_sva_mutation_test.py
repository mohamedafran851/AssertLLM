from pathlib import Path
import subprocess
import shutil

PROJECT_DIR = Path(__file__).resolve().parent.parent

RTL = PROJECT_DIR / "rtl" / "counter.v"
BUGGY_RTL = PROJECT_DIR / "mutations" / "counter_bug.v"
TESTBENCH = PROJECT_DIR / "testbench" / "counter_sva_generated_tb.sv"
GENERATED_DIR = PROJECT_DIR / "generated"


def run_command(command):
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR
    )


def test_design(name, rtl_file, expected_pass):

    print(f"\n===== Testing {name} =====")

    build_dir = PROJECT_DIR / f"obj_ai_{name}"

    if build_dir.exists():
        shutil.rmtree(build_dir)

    compile_command = [
        "verilator",
        "--binary",
        "--timing",
        "--assert",
        "-Wall",
        "-Wno-fatal",
        f"-I{GENERATED_DIR}",
        "--Mdir",
        str(build_dir),
        "--top-module",
        "counter_sva_generated_tb",
        str(rtl_file),
        str(TESTBENCH)
    ]

    compilation = run_command(compile_command)

    if compilation.returncode != 0:
        print("COMPILATION FAILED")
        print(compilation.stdout)
        print(compilation.stderr)
        return False

    print("Compilation successful.")

    executable = build_dir / "Vcounter_sva_generated_tb"

    simulation = run_command([str(executable)])

    output = simulation.stdout + simulation.stderr

    print(output)

    if expected_pass:
        passed = (
            simulation.returncode == 0
            and "AI-GENERATED SVA TEST COMPLETED" in output
        )
    else:
        passed = (
            simulation.returncode != 0
            and "Assertion failed" in output
        )

    print("RESULT:", "PASS" if passed else "UNEXPECTED RESULT")

    return passed


print("===== AssertLLM AI SVA Mutation Testing =====")

if not RTL.exists() or not BUGGY_RTL.exists():
    raise SystemExit("ERROR: Original or mutated RTL file is missing.")

if not TESTBENCH.exists() or not (GENERATED_DIR / "counter_assertions.sv").exists():
    raise SystemExit("ERROR: Testbench or generated SVA file is missing.")

original_result = test_design("original", RTL, True)
mutant_result = test_design("mutant", BUGGY_RTL, False)

print("\n===== FINAL REPORT =====")

print("Original RTL:", "PASS" if original_result else "FAIL")
print("Mutated RTL:", "DETECTED" if mutant_result else "NOT DETECTED")

if original_result and mutant_result:
    print("\nASSERTLLM AI SVA MUTATION TEST PASSED")
else:
    print("\nASSERTLLM AI SVA MUTATION TEST FAILED")
