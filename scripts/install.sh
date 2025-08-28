#!/bin/bash

# ReliQuary Platform - One-Click Installation Script
# Supports Linux and macOS
# Usage: curl -sSL https://install.reliquary.io | bash

set -e

# Configuration
RELIQUARY_VERSION="${RELIQUARY_VERSION:-latest}"
INSTALL_DIR="${INSTALL_DIR:-/usr/local/bin}"
CONFIG_DIR="${CONFIG_DIR:-$HOME/.reliquary}"
TEMP_DIR="/tmp/reliquary-install"
GITHUB_REPO="reliquary/reliquary-platform"
BINARY_NAME="reliquary"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    if [[ "${DEBUG:-}" == "1" ]]; then
        echo -e "${PURPLE}[DEBUG]${NC} $1"
    fi
}

# Print banner
print_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
╦═╗┌─┐┬  ┬╔═╗┬ ┬┌─┐┬─┐┬ ┬
╠╦╝├┤ │  │║═╬╗│ │├─┤├┬┘└┬┘
╩╚═└─┘┴─┘┴╚═╝╚└─┘┴ ┴┴└─ ┴ 
                            
Enterprise-Grade Cryptographic Memory Platform
Post-Quantum • Multi-Agent • Zero-Knowledge
EOF
    echo -e "${NC}"
    echo -e "${GREEN}Installing ReliQuary Platform...${NC}"
    echo ""
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warn "Running as root. Installation will be system-wide."
        INSTALL_DIR="/usr/local/bin"
        CONFIG_DIR="/etc/reliquary"
    else
        log_info "Running as regular user. Installation will be user-specific."
        INSTALL_DIR="$HOME/.local/bin"
        CONFIG_DIR="$HOME/.reliquary"
    fi
}

# Detect operating system and architecture
detect_platform() {
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    
    case $OS in
        linux*)
            OS="linux"
            ;;
        darwin*)
            OS="darwin"
            ;;
        *)
            log_error "Unsupported operating system: $OS"
            exit 1
            ;;
    esac
    
    case $ARCH in
        x86_64|amd64)
            ARCH="amd64"
            ;;
        arm64|aarch64)
            ARCH="arm64"
            ;;
        armv7l)
            ARCH="armv7"
            ;;
        *)
            log_error "Unsupported architecture: $ARCH"
            exit 1
            ;;
    esac
    
    PLATFORM="${OS}_${ARCH}"
    log_info "Detected platform: $PLATFORM"
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check available space (minimum 1GB)
    if command -v df >/dev/null 2>&1; then
        available_space=$(df /tmp | awk 'NR==2 {print $4}')
        if [[ $available_space -lt 1048576 ]]; then # 1GB in KB
            log_error "Insufficient disk space. Need at least 1GB free."
            exit 1
        fi
    fi
    
    # Check memory (minimum 2GB)
    if command -v free >/dev/null 2>&1; then
        total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
        if [[ $total_mem -lt 2 ]]; then
            log_error "Insufficient memory. Need at least 2GB RAM."
            exit 1
        fi
    elif [[ "$OS" == "darwin" ]]; then
        total_mem=$(sysctl -n hw.memsize | awk '{printf "%.0f", $1/1024/1024/1024}')
        if [[ $total_mem -lt 2 ]]; then
            log_error "Insufficient memory. Need at least 2GB RAM."
            exit 1
        fi
    fi
    
    log_success "System requirements check passed"
}

# Check and install dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    local missing_deps=()
    
    # Required tools
    local required_tools=("curl" "tar" "gzip")
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_deps+=("$tool")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        log_info "Please install them using your package manager:"
        
        case $OS in
            linux)
                if command -v apt-get >/dev/null 2>&1; then
                    echo "  sudo apt-get update && sudo apt-get install ${missing_deps[*]}"
                elif command -v yum >/dev/null 2>&1; then
                    echo "  sudo yum install ${missing_deps[*]}"
                elif command -v dnf >/dev/null 2>&1; then
                    echo "  sudo dnf install ${missing_deps[*]}"
                fi
                ;;
            darwin)
                echo "  brew install ${missing_deps[*]}"
                ;;
        esac
        exit 1
    fi
    
    log_success "All dependencies satisfied"
}

# Get latest release version
get_latest_version() {
    if [[ "$RELIQUARY_VERSION" == "latest" ]]; then
        log_info "Fetching latest version..."
        RELIQUARY_VERSION=$(curl -sSf "https://api.github.com/repos/$GITHUB_REPO/releases/latest" | \
            grep '"tag_name":' | \
            sed -E 's/.*"([^"]+)".*/\1/' | \
            sed 's/^v//')
        
        if [[ -z "$RELIQUARY_VERSION" ]]; then
            log_error "Failed to fetch latest version"
            exit 1
        fi
        
        log_info "Latest version: $RELIQUARY_VERSION"
    fi
}

# Download and install binary
download_and_install() {
    log_info "Downloading ReliQuary v$RELIQUARY_VERSION for $PLATFORM..."
    
    # Create temp directory
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    
    # Download URL
    DOWNLOAD_URL="https://github.com/$GITHUB_REPO/releases/download/v$RELIQUARY_VERSION/reliquary-v$RELIQUARY_VERSION-$PLATFORM.tar.gz"
    
    log_debug "Download URL: $DOWNLOAD_URL"
    
    # Download archive
    if ! curl -sSfL "$DOWNLOAD_URL" -o "reliquary.tar.gz"; then
        log_error "Failed to download ReliQuary"
        log_error "URL: $DOWNLOAD_URL"
        exit 1
    fi
    
    # Extract archive
    log_info "Extracting archive..."
    if ! tar -xzf "reliquary.tar.gz"; then
        log_error "Failed to extract archive"
        exit 1
    fi
    
    # Create install directory
    mkdir -p "$INSTALL_DIR"
    
    # Install binary
    log_info "Installing binary to $INSTALL_DIR..."
    if [[ $EUID -eq 0 ]] || [[ "$INSTALL_DIR" == "$HOME"* ]]; then
        cp "$BINARY_NAME" "$INSTALL_DIR/"
        chmod +x "$INSTALL_DIR/$BINARY_NAME"
    else
        sudo cp "$BINARY_NAME" "$INSTALL_DIR/"
        sudo chmod +x "$INSTALL_DIR/$BINARY_NAME"
    fi
    
    log_success "Binary installed successfully"
}

# Setup configuration
setup_config() {
    log_info "Setting up configuration..."
    
    # Create config directory
    mkdir -p "$CONFIG_DIR"
    
    # Create default configuration
    cat > "$CONFIG_DIR/config.yaml" << EOF
# ReliQuary Platform Configuration
# Generated by installer on $(date)

# API Configuration
api:
  endpoint: "https://api.reliquary.io"
  timeout: 30s
  retries: 3

# Authentication
auth:
  # Set your API key here or use RELIQUARY_API_KEY environment variable
  api_key: ""
  
# Logging
logging:
  level: "info"
  format: "json"
  file: "$CONFIG_DIR/reliquary.log"

# Local Settings
local:
  data_dir: "$CONFIG_DIR/data"
  cache_dir: "$CONFIG_DIR/cache"
  temp_dir: "$CONFIG_DIR/tmp"

# Security
security:
  tls_verify: true
  allowed_origins: []
  
# Performance
performance:
  workers: 4
  max_connections: 100
  timeout: "30s"
EOF

    # Create data directories
    mkdir -p "$CONFIG_DIR"/{data,cache,tmp,logs}
    
    # Set permissions
    chmod 700 "$CONFIG_DIR"
    chmod 600 "$CONFIG_DIR/config.yaml"
    
    log_success "Configuration created at $CONFIG_DIR/config.yaml"
}

# Setup systemd service (Linux only)
setup_service() {
    if [[ "$OS" != "linux" ]] || [[ $EUID -ne 0 ]]; then
        return 0
    fi
    
    log_info "Setting up systemd service..."
    
    cat > /etc/systemd/system/reliquary.service << EOF
[Unit]
Description=ReliQuary Platform Service
Documentation=https://docs.reliquary.io
After=network.target
Wants=network.target

[Service]
Type=simple
User=reliquary
Group=reliquary
ExecStart=$INSTALL_DIR/$BINARY_NAME server --config $CONFIG_DIR/config.yaml
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=mixed
Restart=always
RestartSec=5s

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$CONFIG_DIR

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

    # Create reliquary user
    if ! id "reliquary" &>/dev/null; then
        useradd --system --home-dir "$CONFIG_DIR" --shell /bin/false reliquary
        chown -R reliquary:reliquary "$CONFIG_DIR"
    fi
    
    # Enable service
    systemctl daemon-reload
    systemctl enable reliquary.service
    
    log_success "Systemd service configured"
}

# Update PATH
update_path() {
    local shell_rc=""
    
    case "$SHELL" in
        */bash)
            shell_rc="$HOME/.bashrc"
            ;;
        */zsh)
            shell_rc="$HOME/.zshrc"
            ;;
        */fish)
            shell_rc="$HOME/.config/fish/config.fish"
            ;;
    esac
    
    if [[ -n "$shell_rc" ]] && [[ "$INSTALL_DIR" == "$HOME"* ]]; then
        if ! grep -q "$INSTALL_DIR" "$shell_rc" 2>/dev/null; then
            echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$shell_rc"
            log_info "Added $INSTALL_DIR to PATH in $shell_rc"
            log_warn "Please run 'source $shell_rc' or restart your terminal"
        fi
    fi
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    if command -v "$BINARY_NAME" >/dev/null 2>&1; then
        local version=$($BINARY_NAME --version 2>/dev/null || echo "unknown")
        log_success "ReliQuary installed successfully: $version"
    elif [[ -x "$INSTALL_DIR/$BINARY_NAME" ]]; then
        local version=$("$INSTALL_DIR/$BINARY_NAME" --version 2>/dev/null || echo "unknown")
        log_success "ReliQuary installed at $INSTALL_DIR/$BINARY_NAME: $version"
    else
        log_error "Installation verification failed"
        exit 1
    fi
}

# Cleanup
cleanup() {
    log_info "Cleaning up..."
    rm -rf "$TEMP_DIR"
}

# Print next steps
print_next_steps() {
    echo ""
    echo -e "${GREEN}🎉 Installation completed successfully!${NC}"
    echo ""
    echo -e "${CYAN}Next Steps:${NC}"
    echo "1. Get your API key: https://platform.reliquary.io/api-keys"
    echo "2. Configure your API key:"
    echo "   export RELIQUARY_API_KEY='your_api_key_here'"
    echo "   # or edit $CONFIG_DIR/config.yaml"
    echo ""
    echo "3. Test the installation:"
    echo "   reliquary --version"
    echo "   reliquary health check"
    echo ""
    echo "4. Start using ReliQuary:"
    echo "   reliquary vault store --data 'Hello, World!'"
    echo ""
    echo -e "${CYAN}Documentation:${NC} https://docs.reliquary.io"
    echo -e "${CYAN}Examples:${NC} https://github.com/reliquary/examples"
    echo -e "${CYAN}Support:${NC} https://support.reliquary.io"
    echo ""
    
    if [[ "$OS" == "linux" ]] && [[ $EUID -eq 0 ]]; then
        echo -e "${YELLOW}Service Management:${NC}"
        echo "   sudo systemctl start reliquary    # Start service"
        echo "   sudo systemctl status reliquary   # Check status"
        echo "   sudo systemctl logs reliquary     # View logs"
        echo ""
    fi
}

# Error handler
error_handler() {
    local exit_code=$?
    log_error "Installation failed with exit code $exit_code"
    cleanup
    exit $exit_code
}

# Main installation function
main() {
    # Set error handler
    trap error_handler ERR
    
    print_banner
    check_root
    detect_platform
    check_requirements
    check_dependencies
    get_latest_version
    download_and_install
    setup_config
    setup_service
    update_path
    verify_installation
    cleanup
    print_next_steps
}

# Handle command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            RELIQUARY_VERSION="$2"
            shift 2
            ;;
        --install-dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --config-dir)
            CONFIG_DIR="$2"
            shift 2
            ;;
        --debug)
            DEBUG=1
            shift
            ;;
        --help)
            echo "ReliQuary Installation Script"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --version VERSION     Install specific version (default: latest)"
            echo "  --install-dir DIR     Installation directory (default: /usr/local/bin or ~/.local/bin)"
            echo "  --config-dir DIR      Configuration directory (default: /etc/reliquary or ~/.reliquary)"
            echo "  --debug               Enable debug output"
            echo "  --help                Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  RELIQUARY_VERSION     Version to install"
            echo "  INSTALL_DIR           Installation directory"
            echo "  CONFIG_DIR            Configuration directory"
            echo ""
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run main installation
main "$@"