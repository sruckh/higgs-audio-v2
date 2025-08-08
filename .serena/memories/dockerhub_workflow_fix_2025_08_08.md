# DockerHub Workflow Fix for Higgs Audio V2

## What
Fixed the GitHub Actions workflow to properly push Docker images to DockerHub repository gemneye/higgs-audio instead of GitHub Container Registry.

## Why
The original workflow was configured to push to ghcr.io (GitHub Container Registry) but the project needed to push to DockerHub under the gemneye organization instead.

## How
1. Updated the registry from `ghcr.io` to `docker.io`
2. Changed the image name from `${{ github.repository }}` to `gemneye/higgs-audio`
3. Modified the login credentials to use `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets instead of GitHub's token
4. Updated the login step name from "Log in to Container Registry" to "Log in to DockerHub"

## Files Modified
- `.github/workflows/build-runpod-container.yml` - Updated registry configuration and DockerHub authentication

## Issues
No issues encountered during the modification. The changes are straightforward configuration updates that align with the project's deployment requirements.

## Result
The workflow is now properly configured to push Docker images to the gemneye repository on DockerHub when the appropriate secrets (`DOCKER_USERNAME` and `DOCKER_PASSWORD`) are configured in the GitHub repository settings.