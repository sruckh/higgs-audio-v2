#!/bin/bash

# RunPod Serverless Deployment Script for Higgs Audio V2
# This script sets up and deploys the Higgs Audio model as a RunPod serverless endpoint

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NETWORK_VOLUME_PATH="/runpod-volume/higgs_audio"
VOICE_PROMPTS_PATH="/app/voice_prompts"
MODEL_NAME="bosonai/higgs-audio-v2-generation-3B-base"
TOKENIZER_NAME="bosonai/higgs-audio-v2-tokenizer"

echo -e "${BLUE}🚀 Higgs Audio V2 RunPod Serverless Deployment${NC}"
echo "=================================================="

# Check required tools
check_requirements() {
    echo -e "${YELLOW}📋 Checking requirements...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is required but not installed${NC}"
        exit 1
    fi
    
    if ! command -v aws &> /dev/null; then
        echo -e "${YELLOW}⚠️  AWS CLI not found - S3 upload will be disabled${NC}"
    fi
    
    if [ ! -f "$HOME/.aws/credentials" ]; then
        echo -e "${YELLOW}⚠️  AWS credentials not found - S3 upload will be disabled${NC}"
    fi
    
    echo -e "${GREEN}✅ Requirements check passed${NC}"
}

# Build the Docker container
build_container() {
    echo -e "${YELLOW}🏗️  Building RunPod serverless container...${NC}"
    
    docker build -f Dockerfile.runpod -t higgs-audio-runpod:latest .
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Container built successfully${NC}"
    else
        echo -e "${RED}❌ Container build failed${NC}"
        exit 1
    fi
}

# Test container locally
test_container() {
    echo -e "${YELLOW}🧪 Testing container locally...${NC}"
    
    # Run container in background
    docker run -d --name higgs-audio-test -p 8080:8080 higgs-audio-runpod:latest
    
    # Wait for container to start
    sleep 10
    
    # Test health check
    if curl -f http://localhost:8080/health &>/dev/null; then
        echo -e "${GREEN}✅ Container health check passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Health check endpoint not available - continuing${NC}"
    fi
    
    # Stop test container
    docker stop higgs-audio-test
    docker rm higgs-audio-test
}

# Create deployment configuration
create_config() {
    echo -e "${YELLOW}⚙️  Creating deployment configuration...${NC}"
    
    cat > runpod-config.json << EOF
{
    "name": "higgs-audio-v2-serverless",
    "image": "higgs-audio-runpod:latest",
    "gpu": "NVIDIA GeForce RTX 4090",
    "gpu_count": 1,
    "container_disk_size_gb": 5,
    "network_volume_id": "\${NETWORK_VOLUME_ID}",
    "network_volume_mount_path": "/runpod-volume/higgs_audio",
    "ports": "8080/http",
    "env": {
        "PYTHONPATH": "/app",
        "PYTHONUNBUFFERED": "1",
        "TORCH_HOME": "/app/tmp",
        "HF_HOME": "/app/tmp",
        "TRANSFORMERS_CACHE": "/app/tmp",
        "AWS_ACCESS_KEY_ID": "\${AWS_ACCESS_KEY_ID}",
        "AWS_SECRET_ACCESS_KEY": "\${AWS_SECRET_ACCESS_KEY}",
        "AWS_DEFAULT_REGION": "\${AWS_DEFAULT_REGION:-us-east-1}"
    },
    "volume_mount_path": "/app",
    "request_timeout_ms": 300000,
    "idle_timeout_ms": 300000,
    "startup_timeout_ms": 300000
}
EOF
    
    echo -e "${GREEN}✅ Configuration created: runpod-config.json${NC}"
}

# Create example API test script
create_test_script() {
    echo -e "${YELLOW}📝 Creating test script...${NC}"
    
    cat > test-runpod-api.sh << 'EOF'
#!/bin/bash

# Test script for RunPod Higgs Audio API

API_URL="http://localhost:8080/run"

# Test 1: Basic generation
echo "🧪 Testing basic audio generation..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "transcript": "Hello, this is a test of the Higgs Audio RunPod serverless deployment with voice cloning.",
      "ref_audio": "en_woman",
      "scene_prompt": "warm and friendly tone",
      "temperature": 0.8,
      "top_p": 0.9
    }
  }' | jq .

echo -e "\n"

# Test 2: With S3 upload
if [ ! -z "$AWS_S3_BUCKET" ]; then
    echo "🧪 Testing S3 upload..."
    curl -X POST "$API_URL" \
      -H "Content-Type: application/json" \
      -d "{
        \"input\": {
          \"transcript\": \"This audio will be uploaded to S3.\",
          \"ref_audio\": \"en_man\",
          \"scene_prompt\": \"professional speaking style\",
          \"temperature\": 0.7,
          \"s3_bucket\": \"$AWS_S3_BUCKET\",
          \"s3_key\": \"test/higgs-audio-$(date +%s).wav\"
        }
      }" | jq .
else
    echo "⏭️  Skipping S3 test - set AWS_S3_BUCKET environment variable"
fi

echo -e "\n✅ API tests completed"
EOF
    
    chmod +x test-runpod-api.sh
    echo -e "${GREEN}✅ Test script created: test-runpod-api.sh${NC}"
}

# Create network volume setup script
create_volume_setup() {
    echo -e "${YELLOW}💾 Creating network volume setup script...${NC}"
    
    cat > setup-network-volume.sh << 'EOF'
#!/bin/bash

# Script to setup Higgs Audio models on RunPod network volume

NETWORK_VOLUME_PATH="/runpod-volume/higgs_audio"
MODEL_NAME="bosonai/higgs-audio-v2-generation-3B-base"
TOKENIZER_NAME="bosonai/higgs-audio-v2-tokenizer"

echo "📦 Setting up Higgs Audio models on network volume..."

# Create model directories
mkdir -p "$NETWORK_VOLUME_PATH/bosonai"

echo "📥 Downloading models (this may take a while)..."

# Download main model
if [ ! -d "$NETWORK_VOLUME_PATH/bosonai/higgs-audio-v2-generation-3B-base" ]; then
    echo "Downloading main model: $MODEL_NAME"
    git lfs install
    git clone https://huggingface.co/$MODEL_NAME "$NETWORK_VOLUME_PATH/bosonai/higgs-audio-v2-generation-3B-base"
else
    echo "✅ Main model already exists"
fi

# Download audio tokenizer
if [ ! -d "$NETWORK_VOLUME_PATH/bosonai/higgs-audio-v2-tokenizer" ]; then
    echo "Downloading audio tokenizer: $TOKENIZER_NAME"
    git lfs install
    git clone https://huggingface.co/$TOKENIZER_NAME "$NETWORK_VOLUME_PATH/bosonai/higgs-audio-v2-tokenizer"
else
    echo "✅ Audio tokenizer already exists"
fi

echo "✅ Network volume setup complete!"
echo "Models are available at: $NETWORK_VOLUME_PATH/bosonai/"
EOF
    
    chmod +x setup-network-volume.sh
    echo -e "${GREEN}✅ Volume setup script created: setup-network-volume.sh${NC}"
}

# Main deployment workflow
main() {
    echo -e "${BLUE}🎯 Starting Higgs Audio V2 RunPod Deployment${NC}\n"
    
    check_requirements
    build_container
    test_container
    create_config
    create_test_script
    create_volume_setup
    
    echo -e "\n${GREEN}🎉 RunPod deployment setup completed!${NC}"
    echo -e "\n${BLUE}Next steps:${NC}"
    echo "1. 📦 Setup network volume with models:"
    echo "   ./setup-network-volume.sh"
    echo ""
    echo "2. 🚀 Deploy to RunPod:"
    echo "   - Push container to registry"
    echo "   - Use runpod-config.json for deployment"
    echo ""
    echo "3. 🧪 Test the deployment:"
    echo "   ./test-runpod-api.sh"
    echo ""
    echo "4. 📚 Documentation:"
    echo "   - See README.md for detailed instructions"
    echo "   - Check examples/voice_prompts/ for available voices"
    echo ""
    echo -e "${YELLOW}💡 Tip: Ensure your RunPod network volume has the models before deploying${NC}"
}

# Run main function
main "$@"