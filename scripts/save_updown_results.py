import csv
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports/updown_mutation_results.csv"

results = [
    ("original", "rtl/updown_counter.v", "PASS"),
    ("increment_bug", "mutations/updown_bug_increment.v", "DETECTED"),
    ("decrement_bug", "mutations/updown_bug_decrement.v", "DETECTED"),
    ("direction_bug", "mutations/updown_bug_direction.v", "DETECTED"),
]

REPORT.parent.mkdir(parents=True, exist_ok=True)
file_exists = REPORT.exists()

with open(REPORT, "a", newline="") as file:
    writer = csv.writer(file)

    if not file_exists:
        writer.writerow(["timestamp", "design", "rtl_file", "result"])

    timestamp = datetime.now().isoformat(timespec="seconds")

    for name, rtl_file, result in results:
        writer.writerow([timestamp, name, rtl_file, result])

print("===== UP/DOWN RESULTS SAVED =====")
print(f"Saved to: {REPORT}")
