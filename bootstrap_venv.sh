#!/bin/bash
# Virtual Environment Bootstrap Script for RunPod Serverless - Higgs Audio V2
# This script manages the virtual environment on network volume

set -e

# Configuration
VENV_PATH="/runpod-volume/higgs"
REQUIREMENTS_FILE="/app/requirements.runpod.ultra"
PYTHON_EXEC="/runpod-volume/higgs/bin/python"
PIP_EXEC="/runpod-volume/higgs/bin/pip"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if network volume is accessible
check_network_volume() {
    log "Checking network volume accessibility..."
    
    if [ ! -d "/runpod-volume" ]; then
        log_error "Network volume /runpod-volume is not accessible"
        return 1
    fi
    
    # Test write access
    touch /runpod-volume/test_write.$$ 2>/dev/null
    if [ $? -eq 0 ]; then
        rm -f /runpod-volume/test_write.$$
        log_success "Network volume is accessible and writable"
        return 0
    else
        log_error "Network volume is not writable"
        return 1
    fi
}

# Create virtual environment if it doesn't exist
create_virtual_environment() {
    log "Checking virtual environment..."
    
    if [ -d "$VENV_PATH" ]; then
        log_warning "Virtual environment already exists at $VENV_PATH"
        return 0
    fi
    
    log "Creating virtual environment at $VENV_PATH..."
    
    # Ensure parent directory exists
    mkdir -p $(dirname "$VENV_PATH")
    
    # Create virtual environment
    python3 -m venv "$VENV_PATH"
    
    if [ $? -eq 0 ]; then
        log_success "Virtual environment created successfully"
        return 0
    else
        log_error "Failed to create virtual environment"
        return 1
    fi
}

# Upgrade pip and setuptools in virtual environment
upgrade_pip() {
    log "Upgrading pip and setuptools in virtual environment..."
    
    "$PIP_EXEC" install --no-cache-dir --upgrade pip setuptools wheel
    
    if [ $? -eq 0 ]; then
        log_success "Pip and setuptools upgraded successfully"
        return 0
    else
        log_error "Failed to upgrade pip and setuptools"
        return 1
    fi
}

# Install PyTorch with CUDA support
install_pytorch() {
    log "Installing PyTorch with CUDA 12.6 support..."
    
    "$PIP_EXEC" install --no-cache-dir --upgrade-strategy only-if-needed \
        --prefer-binary --no-warn-conflicts \
        torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 \
        --index-url https://download.pytorch.org/whl/cu126
    
    if [ $? -eq 0 ]; then
        log_success "PyTorch installed successfully"
        return 0
    else
        log_error "Failed to install PyTorch"
        return 1
    fi
}

# Install remaining requirements
install_requirements() {
    log "Installing remaining requirements..."
    
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        log_error "Requirements file not found: $REQUIREMENTS_FILE"
        return 1
    fi
    
    "$PIP_EXEC" install --no-cache-dir -r "$REQUIREMENTS_FILE"
    
    if [ $? -eq 0 ]; then
        log_success "Requirements installed successfully"
        return 0
    else
        log_error "Failed to install requirements"
        return 1
    fi
}

# Validate virtual environment setup
validate_virtual_environment() {
    log "Validating virtual environment setup..."
    
    # Check virtual environment structure
    REQUIRED_DIRS=("$VENV_PATH/bin" "$VENV_PATH/lib" "$VENV_PATH/include")
    REQUIRED_FILES=("$PYTHON_EXEC" "$PIP_EXEC")
    
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            log_error "Missing directory: $dir"
            return 1
        fi
    done
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Missing file: $file"
            return 1
        fi
    done
    
    # Test Python executability
    if ! "$PYTHON_EXEC" --version >/dev/null 2>&1; then
        log_error "Python executable is not working"
        return 1
    fi
    
    # Test key package imports
    log "Testing key package imports..."
    
    IMPORT_TEST=$("$PYTHON_EXEC" -c "
import sys
sys.path.insert(0, '/app')

try:
    import torch
    import soundfile
    import transformers
    import loguru
    import boto3
    import numpy
    print('All packages imported successfully')
    print(f'PyTorch version: {torch.__version__}')
    print(f'CUDA available: {torch.cuda.is_available()}')
    exit(0)
except ImportError as e:
    print(f'Import error: {e}')
    exit(1)
except Exception as e:
    print(f'Other error: {e}')
    exit(1)
")
    
    if [ $? -eq 0 ]; then
        log_success "Package imports successful"
        echo "$IMPORT_TEST" | while IFS= read -r line; do
            echo "  $line"
        done
        return 0
    else
        log_error "Package imports failed"
        echo "$IMPORT_TEST" | while IFS= read -r line; do
            echo "  $line"
        done
        return 1
    fi
}

# Calculate space savings
calculate_space_savings() {
    log "Calculating space savings..."
    
    if [ -d "$VENV_PATH" ]; then
        VENV_SIZE=$(du -sh "$VENV_PATH" | cut -f1)
        log_success "Virtual environment size: $VENV_SIZE"
        
        # Compare with estimated system installation size
        ESTIMATED_SYSTEM_SIZE="2.5GB"
        log_info "Estimated system installation size: $ESTIMATED_SYSTEM_SIZE"
        log_success "Space saved by using virtual environment on network volume"
        
        # Calculate actual savings
        VENV_SIZE_BYTES=$(du -sb "$VENV_PATH" | cut -f1)
        SYSTEM_SIZE_BYTES=$(echo "2.5 * 1024 * 1024 * 1024" | bc)
        SAVINGS_BYTES=$((SYSTEM_SIZE_BYTES - VENV_SIZE_BYTES))
        SAVINGS_GB=$(echo "scale=2; $SAVINGS_BYTES / (1024*1024*1024)" | bc)
        log_success "Actual space savings: ${SAVINGS_GB}GB"
    fi
}

# Show virtual environment information
show_virtual_environment_info() {
    log "Virtual Environment Information:"
    echo "  Path: $VENV_PATH"
    echo "  Python: $PYTHON_EXEC"
    echo "  Pip: $PIP_EXEC"
    
    if [ -f "$PYTHON_EXEC" ]; then
        PYTHON_VERSION=$("$PYTHON_EXEC" --version 2>&1)
        echo "  Python Version: $PYTHON_VERSION"
    fi
    
    if [ -d "$VENV_PATH" ]; then
        PACKAGE_COUNT=$("$PIP_EXEC" list | wc -l)
        echo "  Installed Packages: $PACKAGE_COUNT"
    fi
}

# Main setup function
setup_virtual_environment() {
    log "Starting virtual environment setup..."
    
    # Check prerequisites
    if ! check_network_volume; then
        log_error "Network volume check failed"
        exit 1
    fi
    
    # Create virtual environment
    if ! create_virtual_environment; then
        log_error "Virtual environment creation failed"
        exit 1
    fi
    
    # Upgrade pip
    if ! upgrade_pip; then
        log_error "Pip upgrade failed"
        exit 1
    fi
    
    # Install PyTorch
    if ! install_pytorch; then
        log_error "PyTorch installation failed"
        exit 1
    fi
    
    # Install requirements
    if ! install_requirements; then
        log_error "Requirements installation failed"
        exit 1
    fi
    
    # Validate setup
    if ! validate_virtual_environment; then
        log_error "Virtual environment validation failed"
        exit 1
    fi
    
    # Calculate space savings
    calculate_space_savings
    
    # Show final information
    show_virtual_environment_info
    
    log_success "Virtual environment setup completed successfully!"
}

# Command line argument handling
case "${1:-}" in
    "setup")
        setup_virtual_environment
        ;;
    "validate")
        validate_virtual_environment
        ;;
    "info")
        show_virtual_environment_info
        ;;
    "check")
        check_network_volume
        ;;
    *)
        echo "Usage: $0 {setup|validate|info|check}"
        echo ""
        echo "Commands:"
        echo "  setup   - Create and setup virtual environment"
        echo "  validate - Validate existing virtual environment"
        echo "  info    - Show virtual environment information"
        echo "  check   - Check network volume accessibility"
        exit 1
        ;;
esac