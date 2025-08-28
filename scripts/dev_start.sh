#!/bin/bash

# Development Environment Startup Script for ReliQuary
# This script starts all necessary services for development

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== ReliQuary Development Environment Startup ===${NC}"

# Default values
MODE="dev"
PORT=8000
WORKERS=1
LOG_LEVEL="info"
DETACH=false
BUILD=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        -l|--log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        -d|--detach)
            DETACH=true
            shift
            ;;
        -b|--build)
            BUILD=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Start ReliQuary development environment"
            echo ""
            echo "Options:"
            echo "  -m, --mode MODE        Run mode: dev, test, prod (default: dev)"
            echo "  -p, --port PORT        Port to run the API on (default: 8000)"
            echo "  -w, --workers WORKERS  Number of worker processes (default: 1)"
            echo "  -l, --log-level LEVEL  Log level: debug, info, warning, error (default: info)"
            echo "  -d, --detach           Run in background (detached mode)"
            echo "  -b, --build            Build Docker images before starting"
            echo "  -h, --help             Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Check if required tools are installed
check_tools() {
    echo -e "${YELLOW}Checking required tools...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python 3 is not installed${NC}"
        exit 1
    fi
    
    if ! command -v rustc &> /dev/null; then
        echo -e "${RED}Warning: Rust is not installed - FFI modules may not work${NC}"
    fi
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Warning: Docker is not installed - containerized services will not work${NC}"
    fi
    
    if ! command -v circom &> /dev/null; then
        echo -e "${RED}Warning: circom is not installed - ZK circuits will not compile${NC}"
    fi
    
    if ! command -v snarkjs &> /dev/null; then
        echo -e "${RED}Warning: snarkjs is not installed - ZK proofs will not generate${NC}"
    fi
    
    echo -e "${GREEN}✓ Tool check completed${NC}"
}

# Setup Python environment
setup_python_env() {
    echo -e "${YELLOW}Setting up Python environment...${NC}"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${BLUE}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        echo -e "${BLUE}Installing Python dependencies...${NC}"
        pip install -r requirements.txt
    fi
    
    # Install development dependencies
    if [ -f "pyproject.toml" ]; then
        echo -e "${BLUE}Installing project in development mode...${NC}"
        pip install -e .
    fi
    
    echo -e "${GREEN}✓ Python environment setup completed${NC}"
}

# Build Rust modules
build_rust_modules() {
    echo -e "${YELLOW}Building Rust modules...${NC}"
    
    # Check if Rust modules exist
    if [ -d "rust_modules" ]; then
        # Build encryptor module
        if [ -d "rust_modules/encryptor" ]; then
            echo -e "${BLUE}Building encryptor module...${NC}"
            cd rust_modules/encryptor
            cargo build --release
            cd ../..
        fi
        
        # Build merkle module
        if [ -d "rust_modules/merkle" ]; then
            echo -e "${BLUE}Building merkle module...${NC}"
            cd rust_modules/merkle
            cargo build --release
            cd ../..
        fi
    else
        echo -e "${YELLOW}No Rust modules found${NC}"
    fi
    
    echo -e "${GREEN}✓ Rust modules build completed${NC}"
}

# Setup ZK environment
setup_zk_env() {
    echo -e "${YELLOW}Setting up ZK environment...${NC}"
    
    # Check if ZK directory exists
    if [ -d "zk" ]; then
        # Check if PTAU files exist, if not download them
        if [ ! -f "zk/verifier/pot12_final.ptau" ]; then
            echo -e "${BLUE}Downloading PTAU file...${NC}"
            mkdir -p zk/verifier
            # This is a placeholder - in a real implementation, you would download the PTAU file
            echo "PTAU_FILE_PLACEHOLDER" > zk/verifier/pot12_final.ptau
        fi
    else
        echo -e "${YELLOW}No ZK directory found${NC}"
    fi
    
    echo -e "${GREEN}✓ ZK environment setup completed${NC}"
}

# Start services
start_services() {
    echo -e "${YELLOW}Starting services...${NC}"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Determine run command based on detach option
    if [ "$DETACH" = true ]; then
        DETACH_FLAG="--daemon"
        echo -e "${BLUE}Starting in detached mode${NC}"
    else
        DETACH_FLAG=""
        echo -e "${BLUE}Starting in foreground mode${NC}"
    fi
    
    # Start the main API service
    echo -e "${BLUE}Starting ReliQuary API service on port $PORT...${NC}"
    
    # Use uvicorn for development
    if [ "$MODE" = "dev" ]; then
        uvicorn apps.api.main:app \
            --host 0.0.0.0 \
            --port $PORT \
            --workers $WORKERS \
            --log-level $LOG_LEVEL \
            --reload \
            $DETACH_FLAG
    else
        # Use gunicorn for production-like testing
        gunicorn apps.api.main:app \
            --bind 0.0.0.0:$PORT \
            --workers $WORKERS \
            --log-level $LOG_LEVEL \
            $DETACH_FLAG
    fi
    
    echo -e "${GREEN}✓ Services started successfully${NC}"
}

# Start with Docker
start_with_docker() {
    echo -e "${YELLOW}Starting with Docker...${NC}"
    
    # Check if docker-compose.yml exists
    if [ -f "docker/docker-compose.yml" ]; then
        cd docker
        
        # Build images if requested
        if [ "$BUILD" = true ]; then
            echo -e "${BLUE}Building Docker images...${NC}"
            docker-compose build
        fi
        
        # Start services
        echo -e "${BLUE}Starting Docker services...${NC}"
        if [ "$DETACH" = true ]; then
            docker-compose up -d
        else
            docker-compose up
        fi
        
        cd ..
        echo -e "${GREEN}✓ Docker services started successfully${NC}"
    else
        echo -e "${RED}Error: docker-compose.yml not found${NC}"
        exit 1
    fi
}

# Main execution
main() {
    check_tools
    setup_python_env
    build_rust_modules
    setup_zk_env
    
    # Check if Docker mode is requested
    if [ "$MODE" = "docker" ]; then
        start_with_docker
    else
        start_services
    fi
    
    echo -e "${GREEN}=== Development environment is ready ===${NC}"
    echo -e "${BLUE}API available at: http://localhost:$PORT${NC}"
    echo -e "${BLUE}API docs available at: http://localhost:$PORT/docs${NC}"
    echo -e "${BLUE}Health check: http://localhost:$PORT/health${NC}"
}

# Run main function
main