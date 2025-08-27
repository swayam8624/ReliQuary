# zk/verifier/zk_runner.py
import os
import sys
import subprocess
import json
from pathlib import Path

def get_project_root() -> Path:
    """Finds the project root directory in a way that works for scripts and notebooks."""
    try:
        # This works when running as a .py file
        return Path(__file__).parent.parent.parent.resolve()
    except NameError:
        # This is a fallback for interactive environments (like Jupyter)
        # Assumes the notebook is running from the project's root directory.
        return Path.cwd().resolve()

def run_command(command: list, cwd: str = None):
    """
    Runs a shell command and checks for errors.
    """
    print(f"Executing: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Command failed with error code {result.returncode}", file=sys.stderr)
        print("--- STDOUT ---", file=sys.stderr)
        print(result.stdout, file=sys.stderr)
        print("--- STDERR ---", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"Command failed: {' '.join(command)}")
    print("✅ Command successful.")

def run_zk_workflow(circuit_path: Path, input_path: Path):
    """
    Orchestrates the full ZK proof workflow for a given circuit and input.
    """
    project_root = get_project_root()
    verifier_dir = project_root / "zk" / "verifier"
    
    circuit_name = circuit_path.stem
    
    # Create output directories
    build_dir = verifier_dir / "build"
    build_dir.mkdir(exist_ok=True)
    
    print(f"\n--- ZK Workflow for {circuit_name} ---")
    
    # Step 1: Compile the circuit
    run_command(
        ["circom", str(circuit_path), "--wasm", "--r1cs", "-o", str(build_dir)]
    )

    # --- Use the direct groth16 setup command correctly ---
    ptau_path = verifier_dir / "pot12_phase2.ptau"
    if not ptau_path.exists():
        print("❌ Phase 2 Powers of Tau file not found!", file=sys.stderr)
        print(f"Please run: snarkjs pt2 pot12_final.ptau pot12_phase2.ptau", file=sys.stderr)
        print(f"And place it in the '{verifier_dir}' directory.", file=sys.stderr)
        raise FileNotFoundError(f"{ptau_path} not found.")
    
    r1cs_path = build_dir / f"{circuit_name}.r1cs"
    zkey_final = verifier_dir / "circuit_final.zkey"
    vkey_path = verifier_dir / "verification_key.json"
    
    print("\n--- Step 2: Setting up Groth16 ZKey ---")
    # Use groth16 setup directly (as per snarkjs help output)
    run_command(["snarkjs", "groth16", "setup", str(r1cs_path), str(ptau_path), str(zkey_final)], cwd=str(verifier_dir))
    
    print("\n--- Step 3: Exporting Verification Key ---")
    # Export the verification key using the new command format
    run_command(["snarkjs", "zkey", "export", "verificationkey", str(zkey_final), str(vkey_path)], cwd=str(verifier_dir))
    print("✅ ZKey and Verification Key generated.")
    # --- END CORRECT APPROACH ---

    # Step 4: Generate the witness
    print("\n--- Step 4: Generating Witness ---")
    wasm_path = build_dir / f"{circuit_name}_js" / f"{circuit_name}.wasm"
    wtns_path = build_dir / "witness.wtns"
    run_command(["snarkjs", "wtns", "calculate", str(wasm_path), str(input_path), str(wtns_path)], cwd=str(verifier_dir))
    
    # Step 5: Generate the proof
    print("\n--- Step 5: Generating Proof ---")
    proof_path = verifier_dir / "proof.json"
    public_path = verifier_dir / "public.json"
    # Use the final zkey to generate the proof
    run_command(["snarkjs", "groth16", "prove", str(zkey_final), str(wtns_path), str(proof_path), str(public_path)], cwd=str(verifier_dir))
    
    # Step 6: Verify the proof
    print("\n--- Step 6: Verifying Proof ---")
    run_command(["snarkjs", "groth16", "verify", str(vkey_path), str(public_path), str(proof_path)], cwd=str(verifier_dir))

if __name__ == "__main__":
    project_root = get_project_root()
    
    simple_circuit_path = project_root / "zk" / "circuits" / "simple.circom"
    simple_input_path = project_root / "zk" / "examples" / "inputs" / "simple_input.json"
    
    try:
        run_zk_workflow(simple_circuit_path, simple_input_path)
        print("\n🎉🎉🎉 ZK Workflow Completed Successfully! 🎉🎉🎉")
    except (RuntimeError, FileNotFoundError) as e:
        print(f"\n❌ ZK workflow failed. Please check the logs above.", file=sys.stderr)
        print("   Ensure 'circom' and 'snarkjs' are installed and in your PATH.", file=sys.stderr)
        sys.exit(1)
