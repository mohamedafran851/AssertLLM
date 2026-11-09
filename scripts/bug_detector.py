import subprocess

print("===== AssertLLM Bug Detector =====")

# Step 1: Compile RTL and testbench

compile_result = subprocess.run(
    [
        "iverilog",
        "-g2012",
        "-o",
        "counter_sim",
        "../rtl/counter.v",
        "../testbench/counter_tb.sv"
    ],
    capture_output=True,
    text=True
)

# Check compilation

if compile_result.returncode != 0:

    print("COMPILATION ERROR")
    print(compile_result.stderr)

else:

    print("Compilation successful!")

    # Step 2: Run simulation

    simulation = subprocess.run(
        ["vvp", "counter_sim"],
        capture_output=True,
        text=True
    )

    print("\nSimulation output:")
    print(simulation.stdout)

    # Step 3: Analyse result

    if simulation.returncode != 0:
        print("SIMULATION ERROR")

    elif "TEST PASSED" in simulation.stdout:
        print("RESULT: RTL BEHAVIOUR PASSED")

    elif "TEST FAILED" in simulation.stdout:
        print("RESULT: POSSIBLE RTL BUG DETECTED")

    else:
        print("RESULT: INCONCLUSIVE")
