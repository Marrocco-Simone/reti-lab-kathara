#!/usr/bin/env bash

set -e  # Exit on error

echo "=========================================="
echo "  Building DNS Lab Docker Images"
echo "=========================================="
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Build API image
echo "Building API image..."
docker build -t dns-lab/api:latest ./api
echo "✓ API image built successfully"
echo ""

# Build Frontend image
echo "Building Frontend image..."
docker build -t dns-lab/frontend:latest ./frontend
echo "✓ Frontend image built successfully"
echo ""

# Build LLM image
echo "Building LLM image (this will take 10-15 minutes)..."
echo "  - Installing Ollama"
echo "  - Downloading gemma3:270m model (~500MB)"
echo "  Please be patient..."
echo ""
docker build -t dns-lab/llm:latest ./llm
echo "✓ LLM image built successfully (with model pre-downloaded!)"
echo ""

echo "=========================================="
echo "  All images built successfully!"
echo "=========================================="
echo ""
echo "Images created:"
echo "  - dns-lab/api:latest"
echo "  - dns-lab/frontend:latest"
echo "  - dns-lab/llm:latest"
echo ""
echo "You can now start the lab with:"
echo "  bash start-lab.sh"
echo ""
echo "All services will start in ~10 seconds!"
echo "The LLM model is already pre-downloaded in the image."
echo "=========================================="
