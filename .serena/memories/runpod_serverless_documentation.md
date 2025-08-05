# RunPod Serverless Platform Documentation

## Overview
RunPod serverless provides GPU-accelerated container deployment with automatic scaling and pay-per-use pricing. Ideal for ML workloads like audio generation models.

## Container Requirements

### Core Setup
- **Docker**: Engine, CLI, containerd, Docker Compose plugin
- **NVIDIA Container Toolkit**: Required for GPU acceleration
- **Python Packages**: runpod>=0.8.4, CUDA-compatible libraries

### Building Containers

#### Option 1: Using Cog (Recommended)
```bash
# Install Cog CLI
sudo curl -o /usr/local/bin/cog -L https://github.com/replicate/cog/releases/latest/download/cog_`uname -s`_`uname -m`
sudo chmod +x /usr/local/bin/cog

# Build workflow
cog build -t ai-api-{model-name}
docker tag ai-api-{model-name} runpod/ai-api-{model-name}:latest
docker push runpod/ai-api-{model-name}:latest
```

#### Option 2: Standard Docker Build
```bash
docker build --build-arg MODEL_NAME={model-name} -t repo/image_name:tag .
docker tag ait:latest merrell/ait-sd-1-runpod:latest
```

### GPU Container Configuration
```bash
nvidia-docker run --rm -it \
  -e NVIDIA_VISIBLE_DEVICES=0,1,2,3 \
  --shm-size=1g \
  --ulimit memlock=-1 \
  --mount type=bind,src=$PWD,dst=/workspace \
  your-image-name
```

## Interface Specifications

### Input Format
```json
{
  "input": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### Output Format
Structured response compatible with RunPod's serverless interface.

## Testing

### Endpoint Testing
```bash
python test_endpoint.py --endpoint_id={endpoint_id} --key={api_key}
```

### Test Data Structure
```json
{
  "TestInput": {
    "input": {
      "param1": "value1",
      "param2": "value2"
    }
  },
  "TestOutput": {
    "output": {
      "param1": "expected_value1",
      "param2": "expected_value2"
    }
  }
}
```

## Dependencies Example
```
accelerate==0.15.0
bitsandbytes==0.36.0
cog==0.6.1
diffusers==0.12.1
runpod==0.8.4
scipy==1.10.0
transformers==4.26.0
torch==1.13.1
torchvision==0.14.1
```

## Key Requirements for Higgs Audio
1. **Container must accept JSON input** with "input" key
2. **GPU support** with NVIDIA Container Toolkit
3. **Shared memory** (--shm-size=1g) for audio processing
4. **RunPod Python package** (>=0.8.4) for serverless integration
5. **Compatible PyTorch/Transformers** versions
6. **HTTP request handling** on specified port

## Installation Commands Reference
```bash
# Docker + NVIDIA Toolkit
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
```

## Source: Context7 /runpod/serverless-workers documentation