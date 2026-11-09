from pathlib import Path
import csv

PROJECT_DIR = Path(__file__).resolve().parent.parent
CSV_FILE = PROJECT_DIR / "reports/mutation_results.csv"

def calculate_statistics():
    if not CSV_FILE.exists():
        print("ERROR: Mutation results file not found.")
        return

    with open(CSV_FILE, "r", newline="") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        print("No mutation results available.")
        return

    # Count only mutant tests, excluding original RTL.
    mutants = [
        row for row in rows
        if row["design"] != "original"
    ]

    detected = sum(
        row["result"] == "DETECTED" for row in mutants
    )

    not_detected = sum(
        row["result"] == "NOT DETECTED" for row in mutants
    )

    compile_errors = sum(
        row["result"] == "COMPILE ERROR" for row in mutants
    )

    simulation_errors = sum(
        row["result"] == "SIMULATION ERROR" for row in mutants
    )

    valid_mutants = detected + not_detected

    print("\n===== ASSERTLLM MUTATION STATISTICS =====")
    print("Total mutant test records:", len(mutants))
    print("Detected:", detected)
    print("Not detected:", not_detected)
    print("Compile errors:", compile_errors)
    print("Simulation errors:", simulation_errors)

    if valid_mutants:
        rate = detected / valid_mutants * 100
        print(f"Mutation detection rate: {rate:.2f}%")
    else:
        print("Mutation detection rate: N/A")

    print("\n===== ORIGINAL RTL RESULTS =====")

    originals = [
        row for row in rows
        if row["design"] == "original"
    ]

    for row in originals:
        print(row["timestamp"], ":", row["result"])

if __name__ == "__main__":
    calculate_statistics()
