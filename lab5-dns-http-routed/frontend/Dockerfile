FROM kathara/base

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Copy application code to /opt/frontend (will be available in container)
COPY app/ /opt/frontend/app/

EXPOSE 80

# Note: The service will be started by the .startup file
# This allows Kathara to properly configure networking first
