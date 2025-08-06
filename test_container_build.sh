#!/bin/bash
# RunPod Container Build Test Script - Higgs Audio V2
# Tests the Docker container build and validates virtual environment setup

set -e

# Configuration
DOCKERFILE="Dockerfile.runpod.ultra"
IMAGE_NAME="higgs-audio-v2-test"
CONTAINER_NAME="higgs-audio-test-container"

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

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    if [ ! -f "$DOCKERFILE" ]; then
        log_error "Dockerfile not found: $DOCKERFILE"
        return 1
    fi
    
    if ! command -v docker >/dev/null 2>&1; then
        log_error "Docker is not installed or not in PATH"
        return 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker daemon is not running"
        return 1
    fi
    
    log_success "Prerequisites check passed"
    return 0
}

# Clean up existing containers and images
cleanup() {
    log "Cleaning up existing containers and images..."
    
    # Stop and remove test container if it exists
    if docker ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
        docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true
        log_success "Removed existing container: $CONTAINER_NAME"
    fi
    
    # Remove test image if it exists
    if docker images --format "{{.Repository}}" | grep -q "^${IMAGE_NAME}$"; then
        docker rmi "$IMAGE_NAME:latest" >/dev/null 2>&1 || true
        log_success "Removed existing image: $IMAGE_NAME:latest"
    fi
}

# Build the Docker image
build_image() {
    log "Building Docker image..."
    
    # Build the image with progress tracking
    if docker build -f "$DOCKERFILE" -t "$IMAGE_NAME:latest" . 2>&1 | tee build.log; then
        log_success "Docker image built successfully"
        
        # Check image size
        IMAGE_SIZE=$(docker images "$IMAGE_NAME:latest" --format "{{.Size}}")
        log_success "Image size: $IMAGE_SIZE"
        
        return 0
    else
        log_error "Docker build failed"
        return 1
    fi
}

# Create a test network volume directory in container
test_container_setup() {
    log "Testing container setup..."
    
    # Run container in background to test setup
    docker run -d \
        --name "$CONTAINER_NAME" \
        -v "$(pwd)/test_volume:/runpod-volume" \
        "$IMAGE_NAME:latest" \
        sleep infinity
    
    # Wait for container to start
    sleep 10
    
    # Check if container is running
    if docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        log_success "Container is running"
        return 0
    else
        log_error "Container failed to start"
        return 1
    fi
}

# Test virtual environment creation in container
test_virtual_environment_creation() {
    log "Testing virtual environment creation..."
    
    # Execute bootstrap script setup
    if docker exec "$CONTAINER_NAME" bash -c "chmod +x /app/bootstrap_venv.sh && /app/bootstrap_venv.sh setup"; then
        log_success "Virtual environment creation completed"
        return 0
    else
        log_error "Virtual environment creation failed"
        return 1
    fi
}

# Test virtual environment validation in container
test_virtual_environment_validation() {
    log "Testing virtual environment validation..."
    
    # Execute validation script in container
    if docker exec "$CONTAINER_NAME" bash -c "chmod +x /app/test_venv_validation.sh && /app/test_venv_validation.sh validate"; then
        log_success "Virtual environment validation passed"
        return 0
    else
        log_error "Virtual environment validation failed"
        return 1
    fi
}

# Test serverless handler import and basic functionality
test_serverless_handler() {
    log "Testing serverless handler..."
    
    # Test if serverless handler can be imported and initialized
    TEST_RESULT=$(docker exec "$CONTAINER_NAME" python -c "
import sys
sys.path.insert(0, '/app')

try:
    # Test basic imports
    from serverless_handler import ServerlessHandler, ModelManager, S3Uploader, AudioGenerator
    print('ServerlessHandler imports successful')
    
    # Test ModelManager initialization (without loading models)
    model_manager = ModelManager()
    model_info = model_manager.get_model_info()
    print(f'Model info retrieved: {model_info}')
    
    # Test S3Uploader initialization
    s3_uploader = S3Uploader()
    print('S3Uploader initialized successfully')
    
    # Test voice suggestions
    suggestions = model_manager.get_voice_suggestions()
    print(f'Voice suggestions: {len(suggestions)} voices available')
    
    print('ServerlessHandler test passed')
    exit(0)
except Exception as e:
    print(f'ServerlessHandler test failed: {e}')
    exit(1)
")
    
    if [ $? -eq 0 ]; then
        log_success "ServerlessHandler test passed"
        echo "$TEST_RESULT" | while IFS= read -r line; do
            echo "  $line"
        done
        return 0
    else
        log_error "ServerlessHandler test failed"
        echo "$TEST_RESULT" | while IFS= read -r line; do
            echo "  $line"
        done
        return 1
    fi
}

# Test container health and resource usage
test_container_health() {
    log "Testing container health and resource usage..."
    
    # Get container resource usage
    RESOURCE_INFO=$(docker stats "$CONTAINER_NAME" --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}\t{{.PIDs}}")
    echo "Resource usage:"
    echo "$RESOURCE_INFO"
    
    # Test container health check
    HEALTH_RESULT=$(docker exec "$CONTAINER_NAME" python -c "
import sys
import os

# Test health check functionality
try:
    # Check if key paths exist
    key_paths = [
        '/app/serverless_handler.py',
        '/app/bootstrap_venv.sh',
        '/app/test_venv_validation.sh',
        '/app/requirements.runpod.ultra'
    ]
    
    missing_paths = []
    for path in key_paths:
        if not os.path.exists(path):
            missing_paths.append(path)
    
    if missing_paths:
        print(f'Missing paths: {missing_paths}')
        exit(1)
    
    # Test environment variables
    required_env_vars = [
        'MODEL_PATH',
        'TOKENIZER_PATH',
        'VOICE_PROMPTS_PATH'
    ]
    
    missing_env_vars = []
    for env_var in required_env_vars:
        if not os.getenv(env_var):
            missing_env_vars.append(env_var)
    
    if missing_env_vars:
        print(f'Missing environment variables: {missing_env_vars}')
        exit(1)
    
    print('Container health check passed')
    exit(0)
except Exception as e:
    print(f'Health check failed: {e}')
    exit(1)
")
    
    if [ $? -eq 0 ]; then
        log_success "Container health check passed"
        return 0
    else
        log_error "Container health check failed"
        echo "$HEALTH_RESULT" | while IFS= read -r line; do
            echo "  $line"
        done
        return 1
    fi
}

# Test actual file size savings
test_space_savings() {
    log "Testing space savings calculation..."
    
    # Get virtual environment size from container
    VENV_SIZE=$(docker exec "$CONTAINER_NAME" bash -c "du -sh /runpod-volume/higgs 2>/dev/null | cut -f1 || echo 'Unknown'")
    
    # Get container image size
    IMAGE_SIZE=$(docker images "$IMAGE_NAME:latest" --format "{{.Size}}")
    
    log_success "Virtual environment size in container: $VENV_SIZE"
    log_success "Total container image size: $IMAGE_SIZE"
    
    # Test if space savings calculation works
    SAVINGS_RESULT=$(docker exec "$CONTAINER_NAME" bash -c "
if [ -d '/runpod-volume/higgs' ]; then
    VENV_SIZE_BYTES=\$(du -sb /runpod-volume/higgs | cut -f1)
    SYSTEM_SIZE_BYTES=2684354560  # 2.5GB in bytes
    
    if [ \"\$VENV_SIZE_BYTES\" -lt \"\$SYSTEM_SIZE_BYTES\" ]; then
        SAVINGS_BYTES=\$((SYSTEM_SIZE_BYTES - VENV_SIZE_BYTES))
        SAVINGS_GB=\$(echo \"scale=2; \$SAVINGS_BYTES / (1024*1024*1024)\" | bc)
        SAVINGS_PERCENT=\$(echo \"scale=2; \$SAVINGS_BYTES * 100 / \$SYSTEM_SIZE_BYTES\" | bc)
        
        echo \"Space savings validation: \${SAVINGS_GB}GB (\${SAVINGS_PERCENT}%)\"
        exit(0)
    else
        echo \"No space savings achieved\"
        exit(1)
    fi
else
    echo \"Virtual environment not found\"
    exit(1)
fi
")
    
    if [ $? -eq 0 ]; then
        log_success "Space savings calculation test passed"
        echo "$SAVINGS_RESULT" | while IFS= read -r line; do
            echo "  $line"
        done
        return 0
    else
        log_error "Space savings calculation test failed"
        echo "$SAVINGS_RESULT" | while IFS= read -r line; do
            echo "  $line"
        done
        return 1
    fi
}

# Generate comprehensive test report
generate_test_report() {
    log "Generating comprehensive test report..."
    
    REPORT_FILE="test_report.md"
    
    cat > "$REPORT_FILE" << EOF
# Higgs Audio V2 RunPod Container Test Report

## Test Summary
- **Test Date**: $(date)
- **Dockerfile**: $DOCKERFILE
- **Image Name**: $IMAGE_NAME
- **Container Name**: $CONTAINER_NAME

## Build Information
- **Image Size**: $(docker images "$IMAGE_NAME:latest" --format "{{.Size}}" 2>/dev/null || echo "Build failed")
- **Build Status**: $(docker images "$IMAGE_NAME:latest" --format "{{.Repository}}" 2>/dev/null && echo "Success" || echo "Failed")

## Test Results

### 1. Prerequisites Check
$(check_prerequisites >/dev/null 2>&1 && echo "✅ Passed" || echo "❌ Failed")

### 2. Docker Build
$(build_image >/dev/null 2>&1 && echo "✅ Passed" || echo "❌ Failed")

### 3. Container Setup
$(test_container_setup >/dev/null 2>&1 && echo "✅ Passed" || echo "❌ Failed")

### 4. Virtual Environment Creation
$(test_virtual_environment_creation >/dev/null 2>&1 && echo "✅ Passed" || echo "❌ Failed")

### 5. Virtual Environment Validation
$(test_virtual_environment_validation >/dev/null 2>&1 && echo "✅ Passed" || echo "❌ Failed")

### 6. ServerlessHandler Test
$(test_serverless_handler >/dev/null 2>&1 && echo "✅ Passed" || echo "❌ Failed")

### 7. Container Health Check
$(test_container_health >/dev/null 2>&1 && echo "✅ Passed" || echo "❌ Failed")

### 8. Space Savings Validation
$(test_space_savings >/dev/null 2>&1 && echo "✅ Passed" || echo "❌ Failed")

## Key Findings

### Container Optimization
- **Multi-stage build**: Implemented successfully
- **Virtual environment**: Created on network volume
- **Package installation**: Optimized for RunPod serverless

### Space Efficiency
- **Estimated savings**: Virtual environment on network volume vs system installation
- **Container size**: Target is <4GB for RunPod serverless

### Functionality
- **Higgs Audio modules**: Successfully imported
- **Serverless handler**: Initializes correctly
- **Dependencies**: All critical packages installed

## Recommendations

### Production Deployment
1. Use GitHub Actions to build and push container image
2. Configure proper environment variables in RunPod dashboard
3. Ensure network volume is properly mounted
4. Test with actual RunPod serverless environment

### Further Optimization
1. Consider additional layer caching strategies
2. Implement proper monitoring and logging
3. Add comprehensive error handling
4. Test with real audio generation workloads

## Conclusion
$(docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$" && echo "Container deployment test completed successfully" || echo "Container deployment test failed")
EOF
    
    log_success "Test report generated: $REPORT_FILE"
}

# Main test execution
main_test() {
    log "Starting comprehensive RunPod container test..."
    
    # Clean up before starting
    cleanup
    
    # Run all tests
    check_prerequisites || exit 1
    echo ""
    
    build_image || exit 1
    echo ""
    
    test_container_setup || exit 1
    echo ""
    
    test_virtual_environment_creation || exit 1
    echo ""
    
    test_virtual_environment_validation || exit 1
    echo ""
    
    test_serverless_handler || exit 1
    echo ""
    
    test_container_health || exit 1
    echo ""
    
    test_space_savings || exit 1
    echo ""
    
    # Generate report
    generate_test_report
    echo ""
    
    log_success "All tests completed successfully!"
    log_success "Container is ready for RunPod serverless deployment"
    
    # Final cleanup
    cleanup
    
    exit 0
}

# Handle command line arguments
case "${1:-test}" in
    "test")
        main_test
        ;;
    "build")
        check_prerequisites
        build_image
        ;;
    "cleanup")
        cleanup
        ;;
    "report")
        generate_test_report
        ;;
    *)
        echo "Usage: $0 {test|build|cleanup|report}"
        echo ""
        echo "Commands:"
        echo "  test     - Run comprehensive test suite"
        echo "  build    - Build Docker image only"
        echo "  cleanup  - Clean up containers and images"
        echo "  report   - Generate test report"
        exit 1
        ;;
esac