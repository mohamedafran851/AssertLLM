from pathlib import Path
import re

PROJECT_DIR = Path(__file__).resolve().parent.parent
SVA_FILE = PROJECT_DIR / "generated" / "controller_fsm_assertions.sv"

EXPECTED = {
    "reset_property",
    "idle_transition_property",
    "busy_transition_property",
    "done_transition_property",
    "output_property",
    "legal_state_property"
}

print("===== FSM Structural Validator =====")

if not SVA_FILE.exists():
    print("ERROR: Assertion file not found.")
    raise SystemExit(1)

code = SVA_FILE.read_text()

# Remove comments
code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
code = re.sub(r"//.*", "", code)

# Find property blocks
properties = re.findall(
    r"\bproperty\s+(\w+)\s*;(.*?)\bendproperty\b",
    code,
    flags=re.S
)

# Find assertion references
assertions = re.findall(
    r"\bassert\s+property\s*\(\s*(\w+)\s*\)\s*;",
    code,
    flags=re.S
)

property_names = [name for name, body in properties]

valid = True

print("Named properties:", len(properties))
print("Assertions:", len(assertions))

if len(properties) != len(EXPECTED):
    print("ERROR: Incorrect property count.")
    valid = False

if set(property_names) != EXPECTED:
    print("ERROR: Missing or unexpected property names.")
    valid = False

if len(assertions) != len(EXPECTED):
    print("ERROR: Incorrect assertion count.")
    valid = False

if set(assertions) != EXPECTED:
    print("ERROR: Missing or unexpected assertion references.")
    valid = False

if len(set(property_names)) != len(property_names):
    print("ERROR: Duplicate property names.")
    valid = False

if len(set(assertions)) != len(assertions):
    print("ERROR: Duplicate assertion references.")
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

print("Note: Simulation and logical correctness checks are still required.")
