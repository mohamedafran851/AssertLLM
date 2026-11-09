from pathlib import Path
import re

PROJECT_DIR = Path(__file__).resolve().parent.parent
SVA_FILE = PROJECT_DIR / "generated" / "counter_assertions.sv"

print("===== AssertLLM Structural Validator =====")

if not SVA_FILE.exists():
    print("ERROR: Assertion file not found.")
    raise SystemExit(1)

code = SVA_FILE.read_text()

# Remove comments
code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
code = re.sub(r"//.*", "", code)

# Find named property blocks
properties = re.findall(
    r"\bproperty\s+(\w+)\s*;(.*?)\bendproperty\b",
    code,
    flags=re.S
)

# Find assertions, with optional else $error handler
assertions = re.findall(
    r"\bassert\s+property\s*\(\s*(\w+)\s*\)"
    r"(?:\s*else\s+\$error\s*\([^;]*\))?\s*;",
    code,
    flags=re.S
)

print("Named property blocks:", len(properties))
print("Assertions:", len(assertions))

valid = True

if len(properties) != 3:
    print("ERROR: Expected exactly 3 named properties.")
    valid = False

if len(assertions) != 3:
    print("ERROR: Expected exactly 3 assertions.")
    valid = False

property_names = [name for name, body in properties]
assertion_names = assertions

for name, body in properties:
    if not re.search(r"@\s*\(\s*posedge\s+clk\s*\)", body):
        print(f"ERROR: Clock specification missing in {name}.")
        valid = False

    if name not in assertion_names:
        print(f"ERROR: No assertion found for {name}.")
        valid = False

if len(set(property_names)) != len(property_names):
    print("ERROR: Duplicate property names.")
    valid = False

if len(set(assertion_names)) != len(assertion_names):
    print("ERROR: Duplicate assertion references.")
    valid = False

if valid:
    print("\nSTRUCTURAL VALIDATION PASSED")
else:
    print("\nSTRUCTURAL VALIDATION FAILED")
    raise SystemExit(1)

print("Note: Verilator compilation and simulation are still required.")
