from pathlib import Path
from datetime import datetime
import csv

from multi_mutation_test import test_design, DESIGNS

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_DIR / "reports"
CSV_FILE = REPORT_DIR / "mutation_results.csv"

HEADERS = [
    "timestamp",
    "design",
    "rtl_file",
    "result"
]

def initialize_csv():
    REPORT_DIR.mkdir(exist_ok=True)

    if not CSV_FILE.exists():
        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(HEADERS)

def save_results():
    initialize_csv()

    timestamp = datetime.now().isoformat(timespec="seconds")

    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.writer(file)

        for name, rtl_file in DESIGNS.items():
            result = test_design(name, rtl_file)

            writer.writerow([
                timestamp,
                name,
                str(rtl_file.relative_to(PROJECT_DIR)),
                result
            ])

    print("\n===== MUTATION RESULTS SAVED =====")
    print("File:", CSV_FILE)

if __name__ == "__main__":
    save_results()
