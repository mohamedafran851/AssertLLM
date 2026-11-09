from pathlib import Path
import re

PROJECT_DIR = Path(__file__).resolve().parent.parent
SVA_FILE = PROJECT_DIR / "generated" / "updown_counter_assertions.sv"

EXPECTED = {
    "reset_property",
    "up_count_property",
    "down_count_property"
}

print("===== Up/Down Counter Structural Validator =====")

if not SVA_FILE.exists():
    print("ERROR: Assertion file not found.")
    raise SystemExit(1)

code = SVA_FILE.read_text()

code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
code = re.sub(r"//.*", "", code)

properties = re.findall(
    r"\bproperty\s+(\w+)\s*;(.*?)\bendproperty\b",
    code,
    flags=re.S
)

assertions = re.findall(
    r"\bassert\s+property\s*\(\s*(\w+)\s*\)"
    r"(?:\s*else\s+\$error\s*\([^;]*\))?\s*;",
    code,
    flags=re.S
)

property_names = [name for name, body in properties]

valid = True

print("Named properties:", len(properties))
print("Assertions:", len(assertions))

if len(properties) != 3 or set(property_names) != EXPECTED:
    print("ERROR: Property names or count are incorrect.")
    valid = False

if len(assertions) != 3 or set(assertions) != EXPECTED:
    print("ERROR: Assertion references or count are incorrect.")
    valid = False

if len(set(property_names)) != len(property_names):
    print("ERROR: Duplicate property names.")
    valid = False

for name, body in properties:
    if not re.search(r"@\s*\(\s*posedge\s+clk\s*\)", body):
        print(f"ERROR: Clock specification missing in {name}.")
        valid = False

if valid:
    print("\nSTRUCTURAL VALIDATION PASSED")
else:
    print("\nSTRUCTURAL VALIDATION FAILED")
    raise SystemExit(1)

print("Note: Simulation is still required.")
