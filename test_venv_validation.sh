#!/bin/bash
# Virtual Environment Validation Script for RunPod Serverless - Higgs Audio V2
# Tests the virtual environment setup and validates space savings

set -e

# Configuration
VENV_PATH="/runpod-volume/higgs"
PYTHON_EXEC="/runpod-volume/higgs/bin/python"
PIP_EXEC="/runpod-volume/higgs/bin/pip"
REQUIREMENTS_FILE="/app/requirements.runpod.ultra"

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

# Test network volume accessibility
test_network_volume() {
    log "Testing network volume accessibility..."
    
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

# Test virtual environment structure
test_virtual_environment_structure() {
    log "Testing virtual environment structure..."
    
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
    
    log_success "Virtual environment structure is valid"
    return 0
}

# Test Python functionality
test_python_functionality() {
    log "Testing Python functionality..."
    
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
    import librosa
    print('All packages imported successfully')
    print(f'PyTorch version: {torch.__version__}')
    print(f'CUDA available: {torch.cuda.is_available()}')
    print(f'Python version: {sys.version}')
    exit(0)
except ImportError as e:
    print(f'Import error: {e}')
    exit(1)
except Exception as e:
    print(f'Other error: {e}')
    exit(1)
")
    
    if [ $? -eq 0 ]; then
        log_success "Python functionality test passed"
        echo "$IMPORT_TEST" | while IFS= read -r line; do
            echo "  $line"
        done
        return 0
    else
        log_error "Python functionality test failed"
        echo "$IMPORT_TEST" | while IFS= read -r line; do
            echo "  $line"
        done
        return 1
    fi
}

# Test Higgs Audio specific imports
test_higgs_audio_imports() {
    log "Testing Higgs Audio specific imports..."
    
    HIGGS_IMPORT_TEST=$("$PYTHON_EXEC" -c "
import sys
sys.path.insert(0, '/app')

try:
    from boson_multimodal.audio_processing.higgs_audio_tokenizer import load_higgs_audio_tokenizer
    from boson_multimodal.model.higgs_audio.configuration_higgs_audio import HiggsAudioConfig
    from boson_multimodal.model.higgs_audio.modeling_higgs_audio import HiggsAudioModel
    from boson_multimodal.data_collator.higgs_audio_collator import HiggsAudioDataCollator
    from boson_multimodal.dataset.chatml_dataset import ChatMLDataset
    print('Higgs Audio modules imported successfully')
    exit(0)
except ImportError as e:
    print(f'Higgs Audio import error: {e}')
    exit(1)
except Exception as e:
    print(f'Other Higgs Audio error: {e}')
    exit(1)
")
    
    if [ $? -eq 0 ]; then
        log_success "Higgs Audio imports test passed"
        echo "$HIGGS_IMPORT_TEST" | while IFS= read -r line; do
            echo "  $line"
        done
        return 0
    else
        log_error "Higgs Audio imports test failed"
        echo "$HIGGS_IMPORT_TEST" | while IFS= read -r line; do
            echo "  $line"
        done
        return 1
    fi
}

# Test package installation in virtual environment
test_package_installation() {
    log "Testing package installation..."
    
    # Check installed packages
    PACKAGE_COUNT=$("$PIP_EXEC" list | wc -l)
    log_success "Found $PACKAGE_COUNT installed packages"
    
    # Check specific critical packages
    CRITICAL_PACKAGES=("torch" "transformers" "soundfile" "loguru" "boto3" "numpy" "librosa")
    
    for package in "${CRITICAL_PACKAGES[@]}"; do
        if "$PIP_EXEC" show "$package" >/dev/null 2>&1; then
            PACKAGE_VERSION=$("$PIP_EXEC" show "$package" | grep "Version:" | cut -d' ' -f2)
            log_success "Package $package is installed (version: $PACKAGE_VERSION)"
        else
            log_error "Package $package is missing"
            return 1
        fi
    done
    
    log_success "All critical packages are installed correctly"
    return 0
}

# Calculate and validate space savings
validate_space_savings() {
    log "Validating space savings..."
    
    if [ ! -d "$VENV_PATH" ]; then
        log_error "Virtual environment not found at $VENV_PATH"
        return 1
    fi
    
    VENV_SIZE=$(du -sh "$VENV_PATH" | cut -f1)
    VENV_SIZE_BYTES=$(du -sb "$VENV_PATH" | cut -f1)
    
    log_success "Virtual environment size: $VENV_SIZE"
    
    # Compare with estimated system installation size
    ESTIMATED_SYSTEM_SIZE="2.5GB"
    SYSTEM_SIZE_BYTES=$((2684354560))  # 2.5GB in bytes
    
    # Calculate savings
    SAVINGS_BYTES=$((SYSTEM_SIZE_BYTES - VENV_SIZE_BYTES))
    SAVINGS_GB=$(echo "scale=2; $SAVINGS_BYTES / (1024*1024*1024)" | bc 2>/dev/null || echo "N/A")
    
    log_success "Estimated system installation size: $ESTIMATED_SYSTEM_SIZE"
    log_success "Actual space savings: ${SAVINGS_GB}GB"
    
    # Validate that we're saving space
    if [ "$VENV_SIZE_BYTES" -lt "$SYSTEM_SIZE_BYTES" ]; then
        log_success "Space optimization validated - virtual environment is smaller than system installation"
        
        # Calculate percentage savings
        SAVINGS_PERCENT=$(echo "scale=2; $SAVINGS_BYTES * 100 / $SYSTEM_SIZE_BYTES" | bc 2>/dev/null || echo "N/A")
        log_success "Space savings percentage: ${SAVINGS_PERCENT}%"
        
        return 0
    else
        log_warning "Virtual environment is not smaller than estimated system installation"
        return 1
    fi
}

# Test PATH configuration
test_path_configuration() {
    log "Testing PATH configuration..."
    
    # Check if virtual environment Python is in PATH
    if echo "$PATH" | grep -q "/runpod-volume/higgs/bin"; then
        log_success "Virtual environment Python is in PATH"
    else
        log_warning "Virtual environment Python is not in PATH - this may be expected in test environment"
    fi
    
    # Test which Python would be used
    CURRENT_PYTHON=$(which python 2>/dev/null || which python3 2>/dev/null || echo "python not found")
    VENV_PYTHON="$PYTHON_EXEC"
    
    log "Current Python: $CURRENT_PYTHON"
    log "Virtual Environment Python: $VENV_PYTHON"
    
    return 0
}

# Test RunPod compatibility
test_runpod_compatibility() {
    log "Testing RunPod compatibility..."
    
    # Test if we can access the required paths
    MODEL_PATH="/runpod-volume/higgs_audio"
    TOKENIZER_PATH="/runpod-volume/higgs_audio/bosonai/higgs-audio-v2-tokenizer"
    
    log "Checking model paths..."
    
    # Create test directories if they don't exist (for testing purposes)
    mkdir -p "$MODEL_PATH"
    mkdir -p "$(dirname "$TOKENIZER_PATH")"
    
    if [ -w "$MODEL_PATH" ]; then
        log_success "Model path is writable: $MODEL_PATH"
    else
        log_error "Model path is not writable: $MODEL_PATH"
        return 1
    fi
    
    if [ -w "$(dirname "$TOKENIZER_PATH")" ]; then
        log_success "Tokenizer path parent directory is writable: $(dirname "$TOKENIZER_PATH")"
    else
        log_error "Tokenizer path parent directory is not writable: $(dirname "$TOKENIZER_PATH")"
        return 1
    fi
    
    log_success "RunPod compatibility test passed"
    return 0
}

# Main validation function
main_validation() {
    log "Starting comprehensive virtual environment validation..."
    
    # Track overall success
    OVERALL_SUCCESS=true
    
    # Run all validation tests
    test_network_volume || OVERALL_SUCCESS=false
    echo ""
    
    test_virtual_environment_structure || OVERALL_SUCCESS=false
    echo ""
    
    test_python_functionality || OVERALL_SUCCESS=false
    echo ""
    
    test_higgs_audio_imports || OVERALL_SUCCESS=false
    echo ""
    
    test_package_installation || OVERALL_SUCCESS=false
    echo ""
    
    test_path_configuration || OVERALL_SUCCESS=false
    echo ""
    
    validate_space_savings || OVERALL_SUCCESS=false
    echo ""
    
    test_runpod_compatibility || OVERALL_SUCCESS=false
    echo ""
    
    # Summary
    if [ "$OVERALL_SUCCESS" = true ]; then
        log_success "All validation tests passed!"
        log_success "Virtual environment configuration is ready for RunPod serverless deployment"
        exit 0
    else
        log_error "Some validation tests failed"
        exit 1
    fi
}

# Command line argument handling
case "${1:-validate}" in
    "validate")
        main_validation
        ;;
    "network")
        test_network_volume
        ;;
    "structure")
        test_virtual_environment_structure
        ;;
    "python")
        test_python_functionality
        ;;
    "higgs")
        test_higgs_audio_imports
        ;;
    "packages")
        test_package_installation
        ;;
    "space")
        validate_space_savings
        ;;
    "path")
        test_path_configuration
        ;;
    "runpod")
        test_runpod_compatibility
        ;;
    *)
        echo "Usage: $0 {validate|network|structure|python|higgs|packages|space|path|runpod}"
        echo ""
        echo "Commands:"
        echo "  validate     - Run all validation tests"
        echo "  network     - Test network volume accessibility"
        echo "  structure   - Test virtual environment structure"
        echo "  python      - Test Python functionality"
        echo "  higgs       - Test Higgs Audio specific imports"
        echo "  packages    - Test package installation"
        echo "  space       - Validate space savings"
        echo "  path        - Test PATH configuration"
        echo "  runpod      - Test RunPod compatibility"
        exit 1
        ;;
esac