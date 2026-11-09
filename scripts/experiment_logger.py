from pathlib import Path
import csv
from datetime import datetime

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_DIR / "reports"

REPORT_DIR.mkdir(exist_ok=True)

CSV_FILE = REPORT_DIR / "experiment_results.csv"

HEADERS = [
    "experiment_id",
    "timestamp",
    "design",
    "llm_model",
    "assertions_generated",
    "compilation",
    "original_result",
    "mutation_result",
    "overall_result"
]


def initialize_csv():
    if not CSV_FILE.exists():
        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(HEADERS)


def log_experiment(
    design,
    llm_model,
    assertions_generated,
    compilation,
    original_result,
    mutation_result
):
    initialize_csv()

    overall = (
        "PASS"
        if compilation == "PASS"
        and original_result == "PASS"
        and mutation_result == "DETECTED"
        else "FAIL"
    )

    experiment_id = f"EXP-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    row = [
        experiment_id,
        datetime.now().isoformat(timespec="seconds"),
        design,
        llm_model,
        assertions_generated,
        compilation,
        original_result,
        mutation_result,
        overall
    ]

    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(row)

    print("\n===== EXPERIMENT LOGGED =====")
    print("Experiment ID:", experiment_id)
    print("Design:", design)
    print("Overall result:", overall)
    print("Saved to:", CSV_FILE)


if __name__ == "__main__":
    log_experiment(
        design="4-bit counter",
        llm_model="Qwen2.5-Coder:3b",
        assertions_generated=3,
        compilation="PASS",
        original_result="PASS",
        mutation_result="DETECTED"
    )
