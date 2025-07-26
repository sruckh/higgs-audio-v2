"""
Deployment script for Runpod serverless.
Builds and optionally pushes the Docker image.
"""

import os
import subprocess
import sys
import time
import argparse
from loguru import logger


def run_command(cmd: str, description: str) -> bool:
    """
    Run a shell command and log the result.
    
    Args:
        cmd: Command to run
        description: Description for logging
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Running: {description}")
    logger.info(f"Command: {cmd}")
    
    start_time = time.time()
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    duration = time.time() - start_time
    
    if result.returncode == 0:
        logger.info(f"✅ {description} completed in {duration:.1f}s")
        if result.stdout:
            logger.info(f"Output: {result.stdout.strip()}")
        return True
    else:
        logger.error(f"❌ {description} failed (exit code: {result.returncode})")
        if result.stderr:
            logger.error(f"Error: {result.stderr.strip()}")
        if result.stdout:
            logger.error(f"Output: {result.stdout.strip()}")
        return False


def build_docker_image(image_name: str, tag: str = "latest") -> bool:
    """
    Build the Docker image for Runpod serverless.
    
    Args:
        image_name: Name for the Docker image
        tag: Tag for the image
        
    Returns:
        True if successful, False otherwise
    """
    full_image_name = f"{image_name}:{tag}"
    
    # Change to project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    logger.info(f"Building Docker image: {full_image_name}")
    logger.info(f"Build context: {project_root}")
    
    # Build command
    cmd = f"docker build -f runpod_serverless/Dockerfile -t {full_image_name} ."
    
    return run_command(cmd, f"Docker build for {full_image_name}")


def push_docker_image(image_name: str, tag: str = "latest") -> bool:
    """
    Push the Docker image to registry.
    
    Args:
        image_name: Name of the Docker image
        tag: Tag of the image
        
    Returns:
        True if successful, False otherwise
    """
    full_image_name = f"{image_name}:{tag}"
    
    logger.info(f"Pushing Docker image: {full_image_name}")
    
    cmd = f"docker push {full_image_name}"
    
    return run_command(cmd, f"Docker push for {full_image_name}")


def test_image_locally(image_name: str, tag: str = "latest") -> bool:
    """
    Test the Docker image locally.
    
    Args:
        image_name: Name of the Docker image
        tag: Tag of the image
        
    Returns:
        True if successful, False otherwise
    """
    full_image_name = f"{image_name}:{tag}"
    
    logger.info(f"Testing Docker image locally: {full_image_name}")
    
    # Test basic container startup
    cmd = f"docker run --rm --gpus all {full_image_name} python -c \"from runpod_serverless.model_loader import is_ready; print('Container startup test passed')\""
    
    return run_command(cmd, f"Local test for {full_image_name}")


def get_image_size(image_name: str, tag: str = "latest") -> bool:
    """
    Get the size of the built Docker image.
    
    Args:
        image_name: Name of the Docker image
        tag: Tag of the image
        
    Returns:
        True if successful, False otherwise
    """
    full_image_name = f"{image_name}:{tag}"
    
    cmd = f"docker images {full_image_name} --format \"table {{{{.Repository}}}}\\t{{{{.Tag}}}}\\t{{{{.Size}}}}\""
    
    return run_command(cmd, f"Image size for {full_image_name}")


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="Deploy Higgs Audio V2 to Runpod Serverless")
    parser.add_argument("--image-name", required=True, help="Docker image name (e.g., your-registry/higgs-audio-serverless)")
    parser.add_argument("--tag", default="latest", help="Docker image tag")
    parser.add_argument("--push", action="store_true", help="Push image to registry after building")
    parser.add_argument("--test", action="store_true", help="Test image locally after building")
    parser.add_argument("--skip-build", action="store_true", help="Skip building (only push/test)")
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting Runpod Serverless deployment...")
    logger.info(f"Image: {args.image_name}:{args.tag}")
    logger.info(f"Options: push={args.push}, test={args.test}, skip_build={args.skip_build}")
    
    success = True
    
    # Build image
    if not args.skip_build:
        logger.info("\n📦 Building Docker image...")
        if not build_docker_image(args.image_name, args.tag):
            logger.error("Docker build failed!")
            return False
        
        # Get image size
        get_image_size(args.image_name, args.tag)
    
    # Test locally
    if args.test:
        logger.info("\n🧪 Testing image locally...")
        if not test_image_locally(args.image_name, args.tag):
            logger.error("Local test failed!")
            success = False
    
    # Push to registry
    if args.push and success:
        logger.info("\n☁️  Pushing to registry...")
        if not push_docker_image(args.image_name, args.tag):
            logger.error("Docker push failed!")
            success = False
    
    if success:
        logger.info("\n✅ Deployment completed successfully!")
        logger.info(f"Image ready: {args.image_name}:{args.tag}")
        logger.info("\n📋 Next steps:")
        logger.info("1. Create a new Runpod serverless endpoint")
        logger.info(f"2. Set Docker image to: {args.image_name}:{args.tag}")
        logger.info("3. Configure GPU: 24GB+ recommended (A100/H100)")
        logger.info("4. Set environment variables as needed")
        logger.info("5. Test with the API endpoints")
    else:
        logger.error("\n❌ Deployment failed!")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)