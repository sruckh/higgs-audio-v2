# DockerHub Description Setup

This directory contains the DockerHub repository description and metadata that gets automatically updated when the Docker image is built and pushed via GitHub Actions.

## Files

- **`description.md`** - Full DockerHub repository description with comprehensive API documentation
- **`short-description.txt`** - Short description (max 100 characters) for DockerHub repository overview

## Automatic Updates

The GitHub Actions workflow (`.github/workflows/docker-build-push.yml`) automatically updates the DockerHub repository description when:

1. Code is pushed to the `main` branch
2. The Docker image build and push is successful
3. The action uses the `peter-evans/dockerhub-description@v4` action

## DockerHub Repository

- **Repository**: `gemneye/higgs-audio-v2`
- **Registry**: `docker.io`
- **Auto-updated**: ✅ On main branch pushes

## Manual Update

To manually update the DockerHub description:

```bash
# Install dockerhub-description tool
npm install -g dockerhub-description

# Update description
dockerhub-description \
  --username YOUR_USERNAME \
  --password YOUR_PASSWORD \
  --repository gemneye/higgs-audio-v2 \
  --readme .dockerhub/description.md \
  --short-description "$(cat .dockerhub/short-description.txt)"
```

## Content Guidelines

### Full Description (`description.md`)
- **Project overview** with key features
- **Quick start** instructions
- **Complete API documentation** with examples for all 6 endpoints
- **Configuration options** and environment variables
- **Response format** specifications
- **Deployment examples** for various platforms
- **Performance benchmarks** and requirements
- **Links** to documentation and resources

### Short Description (`short-description.txt`)
- **Maximum 100 characters**
- **Concise project summary** with key capabilities
- **No markdown formatting** (plain text only)
- **Include key terms**: AI, audio generation, voice cloning, Docker

## GitHub Secrets Required

The following secrets must be configured in the GitHub repository:

- `DOCKER_USERNAME` - DockerHub username
- `DOCKER_PASSWORD` - DockerHub password or access token

## Notes

- Description only updates on successful builds to `main` branch
- Both images (`higgs-audio-v2` and `higgs-audio-v2-vllm`) use the same description
- The description includes comprehensive endpoint documentation with working examples
- Performance benchmarks and hardware requirements are clearly specified