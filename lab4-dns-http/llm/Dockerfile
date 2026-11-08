FROM kathara/base

# Install Python, pip, and curl
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl zstd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install Python packages
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Pre-download the LLM model during build
# Start Ollama in background, pull model, then stop
RUN ollama serve & \
    sleep 10 && \
    ollama pull gemma3:270m && \
    pkill ollama

# Copy application code to /opt/llm (will be available in container)
COPY app/ /opt/llm/app/

# Expose ports (11434 for Ollama, 80 for FastAPI)
EXPOSE 80 11434

# Note: The service will be started by the .startup file
# This allows Kathara to properly configure networking first
