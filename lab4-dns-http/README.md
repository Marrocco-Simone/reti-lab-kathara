# Networking - DNS Lab with Service Integration

This lab demonstrates a hierarchical DNS system with practical service examples, allowing students to observe DNS resolution, HTTP requests, and streaming protocols using Wireshark.

## Network Topology

### DNS Hierarchy

- **dnsroot** (192.168.0.5) - Root DNS server (.)
- **dnsit** (192.168.0.1) - TLD DNS for .it domain
- **dnsnet** (192.168.0.2) - TLD DNS for .net domain
- **dnsuni** (192.168.0.11) - Authoritative DNS for uniroma3.it
- **dnsstart** (192.168.0.22) - Authoritative DNS for startup.net
- **localuni** (192.168.0.110) - Local DNS server for .it zone
- **localstart** (192.168.0.220) - Local DNS server for .net zone

### Client Machines

- **pc1** (192.168.0.111) - Test client in uniroma3.it domain
- **pc2** (192.168.0.222) - Test client in startup.net domain

### Service Nodes

- **api** (192.168.0.212) - Backend API service (api.startup.net)
- **frontend** (192.168.0.213) - Frontend HTML service (frontend.startup.net)
- **llm** (192.168.0.214) - LLM streaming service (llm.startup.net)

### Monitoring

- **wireshark** - Accessible at localhost:3000

## Quick Start

### 1. Build Docker Images (First Time Only)

Before starting the lab for the first time, build the custom Docker images:

```bash
bash build-images.sh
```

This will build three optimized images with all dependencies pre-installed:

- `dns-lab/api` - Backend API with FastAPI
- `dns-lab/frontend` - Frontend service with FastAPI + httpx
- `dns-lab/llm` - LLM service with Ollama + FastAPI + gemma3:270m model

**Build time**: ~15-20 minutes (includes downloading the ~500MB LLM model)

**Note**: This step only needs to be done once (or when updating service code). The images will be cached locally.

### 2. Start the Lab

```bash
bash start-lab.sh
```

**Fast startup**: All services start in ~10 seconds! Everything (including the LLM model) is pre-installed in the Docker images.

**Note**: The lab network is completely isolated - no internet access required during lab execution. Internet is only needed when building the Docker images.

### 3. Open Wireshark

Open your browser to `localhost:3000` and start capturing packets on **eth1**.

### 4. Basic DNS Resolution Test

Connect to pc1 and resolve pc2.startup.net:

```bash
dig A pc2.startup.net
```

### 5. Test Service DNS Resolution

From pc1, test the new services:

```bash
# Resolve API service
dig A api.startup.net

# Resolve frontend service
dig A frontend.startup.net

# Resolve LLM service
dig A llm.startup.net
```

### 6. Test HTTP Services

From pc1, interact with the services:

```bash
# Get visitor count from backend
curl http://api.startup.net/visitors

# Get HTML from frontend (queries backend via DNS)
curl http://frontend.startup.net/

# Test TCP timeout (wait 10 seconds)
curl http://api.startup.net/delay?seconds=10

# Test large payload (1000000 chars = multi-packet TCP)
curl http://api.startup.net/payload?chars=1000000

# Stream AI response (use underscores for spaces)
curl -N 'http://llm.startup.net/ask?q=What_is_DNS?'

# Alternative: URL-encode spaces as %20
curl -N 'http://llm.startup.net/ask?q=What%20is%20DNS?'
```

**Important**: For LLM questions with spaces, use either:

- Underscores: `What_is_DNS?`
- URL encoding: `What%20is%20DNS?`
- Always wrap the URL in single quotes

## Service Details

### Backend API (api.startup.net)

Provides REST endpoints for testing:

- `GET /visitors` - Returns visitor count
- `GET /delay?seconds=N` - Delays response (TCP timeout testing)
- `GET /payload?chars=N` - Returns large payload (multi-packet testing)

### Frontend (frontend.startup.net)

- Queries backend API via DNS resolution
- Returns HTML page with visitor count
- Demonstrates service-to-service communication

### LLM Service (llm.startup.net)

- Streams AI-generated responses
- Uses gemma3:270m model (very small and fast)
- Demonstrates HTTP streaming protocol
- Use `curl -N` to see streaming in action

## Learning Objectives

1. **DNS Resolution**: Observe hierarchical DNS queries in Wireshark
2. **HTTP Protocol**: Analyze HTTP request/response packets
3. **TCP Behavior**: Study multi-packet transmission and timeout behavior
4. **Streaming Protocols**: Examine chunked transfer encoding
5. **Service Integration**: Understand how services communicate via DNS

## See Also

- [TUTORIAL.md](TUTORIAL.md) - Comprehensive step-by-step guide
- [WIRESHARK_EXERCISES.md](WIRESHARK_EXERCISES.md) - Wireshark analysis exercises
- [SERVICES_GUIDE.md](SERVICES_GUIDE.md) - Detailed API documentation
