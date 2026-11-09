from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

source_file = PROJECT_DIR / "rtl" / "controller_fsm.v"
mutation_dir = PROJECT_DIR / "mutations"

original = source_file.read_text()
mutation_dir.mkdir(exist_ok=True)

mutants = {
    "controller_fsm_bug_start.v": (
        """                if (start)
                    next_state = BUSY;
                else
                    next_state = IDLE;""",
        """                next_state = IDLE;"""
    ),

    "controller_fsm_bug_finish.v": (
        """                if (finish)
                    next_state = DONE;
                else
                    next_state = BUSY;""",
        """                next_state = BUSY;"""
    ),

    "controller_fsm_bug_done.v": (
        """            DONE: begin
                next_state = IDLE;
            end""",
        """            DONE: begin
                next_state = DONE;
            end"""
    ),

    "controller_fsm_bug_outputs.v": (
        """    assign busy = (state == BUSY);
    assign done = (state == DONE);""",
        """    assign busy = (state == DONE);
    assign done = (state == BUSY);"""
    )
}

for filename, (old_code, new_code) in mutants.items():

    if old_code not in original:
        raise ValueError(f"Could not find target code for {filename}")

    mutant_code = original.replace(old_code, new_code, 1)

    output_file = mutation_dir / filename
    output_file.write_text(mutant_code)

    print("Created:", output_file.name)

print("\n===== FSM MUTANTS CREATED =====")
print("Total mutants:", len(mutants))
