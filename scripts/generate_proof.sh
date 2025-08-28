#!/bin/bash

# Zero-Knowledge Proof Generation Script for ReliQuary
# This script generates ZK proofs for testing and development purposes

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== ReliQuary ZK Proof Generation Script ===${NC}"

# Check if required tools are installed
if ! command -v circom &> /dev/null; then
    echo -e "${RED}Error: circom is not installed${NC}"
    echo "Please install circom from https://docs.circom.io/getting-started/installation/"
    exit 1
fi

if ! command -v snarkjs &> /dev/null; then
    echo -e "${RED}Error: snarkjs is not installed${NC}"
    echo "Please install snarkjs: npm install -g snarkjs"
    exit 1
fi

# Default values
CIRCUIT_NAME="device_proof"
INPUT_FILE=""
OUTPUT_DIR="./zk/proofs"
PTAU_FILE="./zk/verifier/pot12_final.ptau"
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--circuit)
            CIRCUIT_NAME="$2"
            shift 2
            ;;
        -i|--input)
            INPUT_FILE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -p|--ptau)
            PTAU_FILE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Generate Zero-Knowledge proofs for ReliQuary"
            echo ""
            echo "Options:"
            echo "  -c, --circuit NAME     Circuit name to use (default: device_proof)"
            echo "  -i, --input FILE       Input JSON file (default: auto-generated)"
            echo "  -o, --output DIR       Output directory (default: ./zk/proofs)"
            echo "  -p, --ptau FILE        PTAU file for trusted setup (default: ./zk/verifier/pot12_final.ptau)"
            echo "  -v, --verbose          Enable verbose output"
            echo "  -h, --help             Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Find circuit file
CIRCUIT_FILE="./zk/circuits/${CIRCUIT_NAME}.circom"
if [ ! -f "$CIRCUIT_FILE" ]; then
    echo -e "${RED}Error: Circuit file not found: $CIRCUIT_FILE${NC}"
    echo "Available circuits:"
    ls ./zk/circuits/*.circom | xargs -n 1 basename | sed 's/\.circom$//'
    exit 1
fi

echo -e "${YELLOW}Using circuit:${NC} $CIRCUIT_NAME"
echo -e "${YELLOW}Circuit file:${NC} $CIRCUIT_FILE"

# Generate input file if not provided
if [ -z "$INPUT_FILE" ]; then
    INPUT_FILE="./zk/proofs/inputs/${CIRCUIT_NAME}_input.json"
    mkdir -p "$(dirname "$INPUT_FILE")"
    
    echo -e "${YELLOW}Generating input file:${NC} $INPUT_FILE"
    
    # Generate sample input based on circuit type
    case $CIRCUIT_NAME in
        "device_proof")
            cat > "$INPUT_FILE" << EOF
{
  "device_fingerprint": "test_device_fingerprint_123456",
  "challenge_nonce": "test_challenge_nonce_7890",
  "timestamp": $(date +%s)
}
EOF
            ;;
        "timestamp_verifier")
            cat > "$INPUT_FILE" << EOF
{
  "current_timestamp": $(date +%s),
  "last_access_time": $(($(date +%s) - 3600)),
  "timezone_offset": 0,
  "require_business_hours": false
}
EOF
            ;;
        "location_chain")
            cat > "$INPUT_FILE" << EOF
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "previous_latitude": 40.7120,
  "previous_longitude": -74.0050,
  "travel_time_hours": 0.5
}
EOF
            ;;
        "pattern_match")
            cat > "$INPUT_FILE" << EOF
{
  "keystrokes_per_minute": 60,
  "access_frequency": 5,
  "session_duration": 1800,
  "is_business_hours": true,
  "location_consistency": true
}
EOF
            ;;
        *)
            # Generic input
            cat > "$INPUT_FILE" << EOF
{
  "input_value": 12345
}
EOF
            ;;
    esac
    
    echo -e "${GREEN}Generated sample input:${NC}"
    cat "$INPUT_FILE"
fi

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo -e "${RED}Error: Input file not found: $INPUT_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}Using input file:${NC} $INPUT_FILE"

# Check if PTAU file exists
if [ ! -f "$PTAU_FILE" ]; then
    echo -e "${RED}Error: PTAU file not found: $PTAU_FILE${NC}"
    echo "Please download or generate the PTAU file first"
    exit 1
fi

echo -e "${YELLOW}Using PTAU file:${NC} $PTAU_FILE"

# Compile circuit
echo -e "${YELLOW}Compiling circuit...${NC}"
circom "$CIRCUIT_FILE" --r1cs --wasm --sym -o "$OUTPUT_DIR"

# Generate witness
echo -e "${YELLOW}Generating witness...${NC}"
node "${OUTPUT_DIR}/${CIRCUIT_NAME}_js/generate_witness.js" \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_js/${CIRCUIT_NAME}.wasm" \
    "$INPUT_FILE" \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_witness.wtns"

# Setup phase 2
echo -e "${YELLOW}Performing phase 2 setup...${NC}"
snarkjs groth16 setup \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}.r1cs" \
    "$PTAU_FILE" \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_0000.zkey"

# Generate final zkey
echo -e "${YELLOW}Generating final zkey...${NC}"
echo "reliquary_zk_test" | snarkjs zkey contribute \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_0000.zkey" \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_final.zkey" \
    --name="ReliQuary Test Contribution"

# Export verification key
echo -e "${YELLOW}Exporting verification key...${NC}"
snarkjs zkey export verificationkey \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_final.zkey" \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_vkey.json"

# Generate proof
echo -e "${YELLOW}Generating proof...${NC}"
snarkjs groth16 prove \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_final.zkey" \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_witness.wtns" \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_proof.json" \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_public.json"

# Verify proof
echo -e "${YELLOW}Verifying proof...${NC}"
if snarkjs groth16 verify \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_vkey.json" \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_public.json" \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_proof.json"; then
    echo -e "${GREEN}✓ Proof verification successful!${NC}"
else
    echo -e "${RED}✗ Proof verification failed!${NC}"
    exit 1
fi

# Generate Solidity verifier (optional)
echo -e "${YELLOW}Generating Solidity verifier (optional)...${NC}"
snarkjs zkey export solidityverifier \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_final.zkey" \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_verifier.sol" 2>/dev/null || echo "Solidity verifier generation skipped"

# Generate call parameters
echo -e "${YELLOW}Generating call parameters...${NC}"
snarkjs generatecall \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_public.json" \
    "${OUTPUT_DIR}/${CIRCUIT_NAME}_proof.json" \
    > "${OUTPUT_DIR}/${CIRCUIT_NAME}_call_params.txt" 2>/dev/null || echo "Call parameters generation skipped"

echo -e "${GREEN}=== Proof generation completed successfully ===${NC}"
echo -e "${GREEN}Proof files generated in:${NC} $OUTPUT_DIR"
echo -e "${GREEN}Proof file:${NC} ${OUTPUT_DIR}/${CIRCUIT_NAME}_proof.json"
echo -e "${GREEN}Public inputs:${NC} ${OUTPUT_DIR}/${CIRCUIT_NAME}_public.json"
echo -e "${GREEN}Verification key:${NC} ${OUTPUT_DIR}/${CIRCUIT_NAME}_vkey.json"

if [ "$VERBOSE" = true ]; then
    echo -e "${YELLOW}Proof content:${NC}"
    cat "${OUTPUT_DIR}/${CIRCUIT_NAME}_proof.json"
    echo -e "${YELLOW}Public inputs:${NC}"
    cat "${OUTPUT_DIR}/${CIRCUIT_NAME}_public.json"
fi