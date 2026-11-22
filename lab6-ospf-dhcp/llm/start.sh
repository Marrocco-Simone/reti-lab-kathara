#!/bin/bash

# Start Ollama service in background
ollama serve &

# Wait for Ollama to be ready
sleep 10

# Pull the model
ollama pull gemma3:270m

# Start the FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port 80
