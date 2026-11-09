
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "reports"

SCRIPTS = [
    "scripts/multi_mutation_test.py",
    "scripts/updown_mutation_test.py",
    "scripts/fsm_mutation_test.py",
    "scripts/alu4_mutation_test.py",
    "scripts/mux4to1_mutation_test.py",
    "scripts/sequence_detector_1011_mutation_test.py",
    "scripts/combined_evaluation.py",
]

def run_script(script):
    print(f"\n{'=' * 60}")
    print(f"RUNNING: {script}")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / script)],
            cwd=ROOT,
            capture_output=True,
            text=True
        )
    except (OSError, subprocess.SubprocessError) as error:
        output = str(error)
        print(f"EXECUTION ERROR: {output}")
        return False, output

    output = result.stdout + result.stderr
    print(output)

    if result.returncode != 0:
        print(f"ERROR: {script} failed.")
        return False, output

    print(f"SUCCESS: {script}")
    return True, output


def main():
    print("===== ASSERTLLM MASTER EVALUATION =====")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now()

    all_outputs = [
        "ASSERTLLM FINAL EVALUATION REPORT",
        f"Date and time: {timestamp.isoformat(timespec='seconds')}",
        "=" * 60,
    ]

    successful = True

    for script in SCRIPTS:
        status, output = run_script(script)

        all_outputs.append(f"\nSCRIPT: {script}")
        all_outputs.append(output)

        if not status:
            successful = False
            all_outputs.append("STATUS: FAILED")
            break

        all_outputs.append("STATUS: SUCCESS")

    if successful:
        print("\n" + "=" * 60)
        print("ALL TESTS AND COMBINED EVALUATION COMPLETED")
        print("=" * 60)

        all_outputs.append("\nMASTER STATUS: PASSED")
    else:
        print("\nMASTER EVALUATION FAILED")
        all_outputs.append("\nMASTER STATUS: FAILED")

    report_name = (
        "final_evaluation_"
        + timestamp.strftime("%Y%m%d_%H%M%S")
        + ".txt"
    )

    report_path = REPORTS_DIR / report_name

    report_path.write_text(
        "\n".join(all_outputs),
        encoding="utf-8"
    )

    print(f"\nFinal report saved to: {report_path}")

    if not successful:
        sys.exit(1)


if __name__ == "__main__":
    main()
