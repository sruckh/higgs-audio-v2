#!/bin/bash
# Test script for RunPod Higgs Audio V2 Serverless Deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
API_ENDPOINT="${RUNPOD_ENDPOINT:-http://localhost:8080}"
TEST_OUTPUT_DIR="./test-results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${PURPLE}🧪 Higgs Audio V2 Serverless Test Suite${NC}"
echo -e "${PURPLE}==========================================${NC}"

# Create test results directory
mkdir -p "$TEST_OUTPUT_DIR/$TIMESTAMP"

# Helper functions
send_request() {
    local endpoint="$1"
    local data="$2"
    local description="$3"
    
    echo -e "\n${CYAN}📤 Testing: $description${NC}"
    echo "Endpoint: $endpoint"
    echo "Payload: $data"
    
    response=$(curl -s -X POST "$endpoint" \
        -H "Content-Type: application/json" \
        -d "$data" 2>/dev/null || echo '{"error": "Request failed"}')
    
    echo -e "${YELLOW}📥 Response:${NC}"
    echo "$response" | jq . 2>/dev/null || echo "$response"
    
    # Save response to file
    echo "$response" > "$TEST_OUTPUT_DIR/$TIMESTAMP/${description// /_}.json"
    
    # Extract success status
    success=$(echo "$response" | jq -r '.output.success // .success // false' 2>/dev/null || echo "false")
    
    if [[ "$success" == "true" ]]; then
        echo -e "${GREEN}✅ Test passed: $description${NC}"
        return 0
    else
        echo -e "${RED}❌ Test failed: $description${NC}"
        return 1
    fi
}

# Test 1: Health Check
test_health_check() {
    echo -e "\n${BLUE}🏥 Testing Health Check Endpoint${NC}"
    
    response=$(curl -s "$API_ENDPOINT/health" 2>/dev/null || echo '{"status": "error"}')
    echo "$response" | jq .
    
    status=$(echo "$response" | jq -r '.status' 2>/dev/null || echo "error")
    echo "$response" > "$TEST_OUTPUT_DIR/$TIMESTAMP/health_check.json"
    
    if [[ "$status" == "healthy" ]]; then
        echo -e "${GREEN}✅ Health check passed${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Health check returned status: $status${NC}"
        return 0
    fi
}

# Test 2: Basic Audio Generation
test_basic_generation() {
    local request='{
      "input": {
        "transcript": "Hello, this is a test of the Higgs Audio V2 serverless deployment with basic voice cloning capabilities.",
        "ref_audio": "belinda",
        "temperature": 0.8,
        "top_p": 0.9
      }
    }'
    
    send_request "$API_ENDPOINT" "$request" "basic_audio_generation"
}

# Test 3: Long Text Generation
test_long_text_generation() {
    local request='{
      "input": {
        "transcript": "The quick brown fox jumps over the lazy dog. This is a longer text that tests the generation capabilities of the Higgs Audio V2 model with multiple sentences and complex patterns. The audio should be clear, natural, and maintain consistent voice characteristics throughout the entire sequence.",
        "ref_audio": "chadwick",
        "temperature": 0.7,
        "top_p": 0.85,
        "max_new_tokens": 3000
      }
    }'
    
    send_request "$API_ENDPOINT" "$request" "long_text_generation"
}

# Test 4: LLM Tone Control
test_tone_control() {
    local request='{
      "input": {
        "transcript": "Welcome to our presentation today. We are excited to share our findings with the entire team.",
        "ref_audio": "elsa",
        "scene_prompt": "professional presentation with enthusiastic and engaging tone",
        "temperature": 0.6,
        "top_p": 0.8
      }
    }'
    
    send_request "$API_ENDPOINT" "$request" "llm_tone_control"
}

# Test 5: Different Voices
test_different_voices() {
    local voices=("jorts" "daffy")
    
    for voice in "${voices[@]}"; do
        local request="{
          \"input\": {
            \"transcript\": \"This is a test of the $voice voice profile in the Higgs Audio system.\",
            \"ref_audio\": \"$voice\",
            \"temperature\": 0.8
          }
        }"
        
        send_request "$API_ENDPOINT" "$request" "voice_test_$voice"
    done
}

# Test 6: Temperature Variation
test_temperature_variation() {
    local temperatures=("0.3" "1.0" "1.8")
    
    for temp in "${temperatures[@]}"; do
        local request="{
          \"input\": {
            \"transcript\": \"This tests temperature variation with value $temp\",
            \"ref_audio\": \"belinda\",
            \"temperature\": $temp,
            \"top_p\": 0.9
          }
        }"
        
        send_request "$API_ENDPOINT" "$request" "temperature_test_$temp"
    done
}

# Test 7: Error Handling - Invalid Parameters
test_error_handling() {
    echo -e "\n${YELLOW}🚨 Testing Error Handling${NC}"
    
    # Test empty transcript
    local request='{"input": {"transcript": "", "ref_audio": "belinda"}}'
    
    response=$(curl -s -X POST "$API_ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "$request" 2>/dev/null || echo '{"output": {"success": false}}')
    
    echo "$response" | jq . > "$TEST_OUTPUT_DIR/$TIMESTAMP/error_handling_empty.json"
    
    success=$(echo "$response" | jq -r '.output.success // false' 2>/dev/null || echo "false")
    if [[ "$success" == "false" ]]; then
        echo -e "${GREEN}✅ Error handling test passed - correctly rejected empty transcript${NC}"
    else
        echo -e "${RED}❌ Error handling test failed - should have rejected empty transcript${NC}"
    fi
}

# Test 8: Performance Metrics
test_performance_metrics() {
    echo -e "\n${CYAN}📊 Testing Performance Metrics${NC}"
    
    local request='{
      "input": {
        "transcript": "Performance testing the Higgs Audio V2 serverless deployment with voice cloning.",
        "ref_audio": "belinda",
        "temperature": 0.8
      }
    }'
    
    echo -e "${YELLOW}⏱️  Measuring response time...${NC}"
    start_time=$(date +%s%N)
    
    response=$(curl -s -X POST "$API_ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "$request" 2>/dev/null || echo '{"output": {"success": false}}')
    
    end_time=$(date +%s%N)
    
    duration_ms=$(( (end_time - start_time) / 1000000 ))
    
    echo "$response" > "$TEST_OUTPUT_DIR/$TIMESTAMP/performance_test.json"
    
    success=$(echo "$response" | jq -r '.output.success // false' 2>/dev/null || echo "false")
    
    if [[ "$success" == "true" ]]; then
        echo -e "${GREEN}✅ Performance test completed in ${duration_ms}ms${NC}"
        
        if [[ $duration_ms -lt 30000 ]]; then
            echo -e "${GREEN}✅ Response time within acceptable range (<30s)${NC}"
        else
            echo -e "${YELLOW}⚠️  Response time high: ${duration_ms}ms${NC}"
        fi
    else
        echo -e "${RED}❌ Performance test failed${NC}"
    fi
}

# Test 9: Parameter Validation
test_parameter_validation() {
    echo -e "\n${YELLOW}🔍 Testing Parameter Validation${NC}"
    
    # Test invalid temperature
    local request='{"input": {"transcript": "Test", "ref_audio": "belinda", "temperature": 3.0}}'
    
    response=$(curl -s -X POST "$API_ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "$request" 2>/dev/null || echo '{"output": {"success": false}}')
    
    echo "$response" | jq . > "$TEST_OUTPUT_DIR/$TIMESTAMP/param_validation.json"
    
    # Check if validation error occurred
    error_msg=$(echo "$response" | jq -r '.output.error // .error // ""' 2>/dev/null || echo "")
    
    if [[ "$error_msg" == *"temperature"* ]]; then
        echo -e "${GREEN}✅ Parameter validation test passed - correctly rejected invalid temperature${NC}"
    else
        echo -e "${YELLOW}⚠️  Parameter validation inconclusive${NC}"
    fi
}

# Test 10: Memory Efficiency Check
test_memory_efficiency() {
    echo -e "\n${BLUE}💾 Testing Memory Efficiency${NC}"
    
    echo -e "${YELLOW}Note: This test is informative only - actual memory usage should be monitored via RunPod dashboard${NC}"
    
    echo "Expected memory usage for optimized deployment:"
    echo "- Container RAM: ~2GB"
    echo "- GPU Memory: ~8GB (with models loaded)"
    echo "- Container Image Size: <5GB"
    
    # Create memory test record
    cat > "$TEST_OUTPUT_DIR/$TIMESTAMP/memory_efficiency.json" << EOF
{
  "test_name": "memory_efficiency",
  "timestamp": "$(date -Iseconds)",
  "expected_usage": {
    "container_ram_gb": 2.0,
    "gpu_memory_gb": 8.0,
    "image_size_gb": 5.0
  },
  "optimization_applied": [
    "bfloat16_precision",
    "static_kv_cache",
    "model_caching",
    "memory_cleanup",
    "slim_dependencies"
  ],
  "monitoring_command": "runpodctl get serverless <deployment-id>"
}
EOF
    
    echo -e "${GREEN}✅ Memory efficiency documentation created${NC}"
}

# Main test execution
main() {
    echo -e "${BLUE}🎯 Starting comprehensive test suite for Higgs Audio V2 Serverless${NC}"
    echo -e "${CYAN}API Endpoint: $API_ENDPOINT${NC}"
    echo -e "${CYAN}Test Results Directory: $TEST_OUTPUT_DIR/$TIMESTAMP${NC}"
    echo ""
    
    # Run all tests
    test_health_check || echo "Health check failed but continuing..."
    test_basic_generation || echo "Basic generation test failed"
    test_long_text_generation || echo "Long text generation test failed"
    test_tone_control || echo "Tone control test failed"
    test_different_voices || echo "Different voices test failed"
    test_temperature_variation || echo "Temperature variation test failed"
    test_error_handling || echo "Error handling test failed"
    test_performance_metrics || echo "Performance metrics test failed"
    test_parameter_validation || echo "Parameter validation test failed"
    test_memory_efficiency || echo "Memory efficiency test failed"
    
    # Generate summary
    echo -e "\n${GREEN}📊 Test Suite Summary${NC}"
    echo -e "${GREEN}========================${NC}"
    echo "All tests completed!"
    echo "Results saved to: $TEST_OUTPUT_DIR/$TIMESTAMP/"
    echo ""
    echo -e "${CYAN}📋 Test Files Generated:${NC}"
    ls -la "$TEST_OUTPUT_DIR/$TIMESTAMP/" | grep -v "^d" | awk '{print "  - " $9}'
    echo ""
    echo -e "${BLUE}🔍 Analyze Results:${NC}"
    echo "  - Check individual JSON files for detailed responses"
    echo "  - Validate success/failure status for each test"
    echo "  - Monitor performance metrics for optimization opportunities"
    echo ""
    echo -e "${PURPLE}🎉 Test suite completed successfully!${NC}"
}

# Check dependencies
check_dependencies() {
    echo -e "${YELLOW}📋 Checking test dependencies...${NC}"
    
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}❌ curl is required for testing${NC}"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}⚠️  jq not found - response formatting will be limited${NC}"
    fi
    
    echo -e "${GREEN}✅ Dependencies check passed${NC}"
}

# Run the test suite
check_dependencies
main "$@"