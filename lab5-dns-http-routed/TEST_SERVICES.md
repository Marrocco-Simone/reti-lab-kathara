# Service Testing Guide

Quick reference for testing all lab services from pc1.

## Connect to pc1

```bash
kathara connect pc1
```

## DNS Resolution Tests

Test that DNS resolves correctly for all services:

```bash
# Test API service
dig A api.startup.net

# Test Frontend service
dig A frontend.startup.net

# Test LLM service
dig A llm.startup.net

# Test cross-domain resolution
dig A pc2.startup.net
```

**Expected Results:**
- api.startup.net → 192.168.0.112
- frontend.startup.net → 192.168.0.113
- llm.startup.net → 192.168.0.114
- pc2.startup.net → 192.168.0.222

## HTTP Service Tests

### Backend API Tests

```bash
# Root endpoint (service info)
curl http://api.startup.net/

# Visitor counter (increments each time)
curl http://api.startup.net/visitors
curl http://api.startup.net/visitors

# Delay test (5 seconds)
curl http://api.startup.net/delay?seconds=5

# Large payload test (multi-packet TCP)
curl http://api.startup.net/payload?chars=50000

# Health check
curl http://api.startup.net/health
```

### Frontend Test

```bash
# Get HTML page (queries backend)
curl http://frontend.startup.net/

# Should return HTML with visitor count
```

### LLM Service Tests

```bash
# Service info
curl http://llm.startup.net/

# Simple question (no spaces - use single quotes)
curl -N 'http://llm.startup.net/ask?q=What_is_DNS?'

# Question with spaces (use %20 for spaces)
curl -N 'http://llm.startup.net/ask?q=Explain%20TCP%20handshake'

# Alternative: use underscores instead of spaces
curl -N 'http://llm.startup.net/ask?q=Explain_TCP_handshake'

# Health check
curl http://llm.startup.net/health
```

**Important Notes:**
- Use `-N` flag with `/ask` endpoint to disable buffering and see streaming
- For questions with spaces: either use `%20` (URL encoding) or `_` (underscores)
- Always wrap the URL in single quotes: `'http://...'`

## Wireshark Analysis

While running the above tests:

1. Open Wireshark at `http://localhost:3000`
2. Start capture on **eth1**
3. Run tests from pc1
4. Observe in Wireshark:
   - DNS queries and responses
   - HTTP requests and responses
   - TCP handshakes (SYN, SYN-ACK, ACK)
   - Multi-packet TCP for large payloads
   - Streaming chunked encoding for LLM

### Useful Filters

```
dns                              # All DNS traffic
dns.qry.name == "api.startup.net"  # Specific domain
http                             # All HTTP traffic
http.request.method == "GET"     # HTTP GET requests
tcp.flags.syn == 1               # TCP SYN packets
tcp.stream eq 0                  # Follow TCP stream
```

## Expected Service Status

All services should show:

```
INFO:     Uvicorn running on http://0.0.0.0:80 (Press CTRL+C to quit)
```

LLM service also shows:
```
time=... level=INFO source=routes.go:... msg="Listening on 127.0.0.1:11434 (version ...)"
```

## Troubleshooting

### Service Not Responding

Check if service is running:
```bash
kathara exec api -- ps aux | grep uvicorn
kathara exec frontend -- ps aux | grep uvicorn
kathara exec llm -- ps aux | grep uvicorn
```

### DNS Not Resolving

Check DNS server:
```bash
kathara exec dnsuni -- systemctl status named
```

Restart if needed:
```bash
kathara exec dnsuni -- systemctl restart named
```

### LLM Not Responding

Check Ollama status:
```bash
kathara exec llm -- ps aux | grep ollama
```

Check if model is loaded:
```bash
kathara exec llm -- ollama list
```

## Success Criteria

✅ All DNS queries resolve correctly
✅ API returns JSON responses
✅ Frontend returns HTML with visitor count
✅ LLM streams responses token-by-token
✅ Wireshark captures all traffic
✅ Services start in ~10 seconds

---

**Everything working?** Congratulations! Your DNS lab is ready for students. 🎓
