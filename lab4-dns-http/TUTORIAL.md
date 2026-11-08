# DNS Lab Tutorial: Complete Guide

This tutorial provides a comprehensive, step-by-step guide to understanding DNS resolution and network protocols using Kathara and Wireshark.

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Lab Architecture](#lab-architecture)
4. [Getting Started](#getting-started)
5. [Part 1: Basic DNS Resolution](#part-1-basic-dns-resolution)
6. [Part 2: Hierarchical DNS](#part-2-hierarchical-dns)
7. [Part 3: HTTP Services](#part-3-http-services)
8. [Part 4: TCP Behavior](#part-4-tcp-behavior)
9. [Part 5: Streaming Protocols](#part-5-streaming-protocols)
10. [Advanced Topics](#advanced-topics)
11. [Troubleshooting](#troubleshooting)

---

## Introduction

### What You Will Learn

This lab teaches fundamental networking concepts through hands-on exercises:

- **DNS Resolution**: How domain names are translated to IP addresses
- **DNS Hierarchy**: Root servers, TLD servers, and authoritative servers
- **HTTP Protocol**: Request/response cycles and headers
- **TCP Protocol**: Connection establishment, data transmission, and timeouts
- **Streaming**: How servers send data incrementally
- **Network Analysis**: Using Wireshark to inspect packets

### Learning Objectives

By the end of this tutorial, you will be able to:
- Configure and understand DNS zone files
- Trace DNS queries through the hierarchy
- Analyze HTTP traffic in Wireshark
- Identify TCP packet patterns
- Understand streaming protocols
- Debug network issues using packet analysis

---

## Prerequisites

### Required Software

- **Kathara**: Container-based network emulation platform
- **Web Browser**: For accessing Wireshark UI
- **Basic Linux Knowledge**: Command-line familiarity

### Recommended Background

- Understanding of IP addresses and subnets
- Basic knowledge of HTTP
- Familiarity with command-line tools (`curl`, `dig`)

---

## Lab Architecture

### Network Topology

```
                    ┌─────────────┐
                    │   dnsroot   │
                    │ 192.168.0.5 │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
        ┌─────▼─────┐            ┌─────▼─────┐
        │   dnsit   │            │  dnsnet   │
        │192.168.0.1│            │192.168.0.2│
        └─────┬─────┘            └─────┬─────┘
              │                        │
        ┌─────▼──────┐          ┌──────▼─────┐
        │  dnsuni    │          │ dnsstart   │
        │192.168.0.11│          │192.168.0.22│
        └─────┬──────┘          └────────────┘
              │
    ┌─────────┼──────────────────┐
    │         │                  │
┌───▼────┐ ┌──▼───┐ ┌─────────▼────┐
│  pc1   │ │ api  │ │   frontend   │
│ .111   │ │ .112 │ │    .113      │
└────────┘ └──────┘ └──────────────┘

                    ┌──────────┐
                    │   llm    │
                    │  .114    │
                    └──────────┘
```

### IP Address Table

| Node | IP Address | Domain Name | Purpose |
|------|-----------|-------------|---------|
| dnsroot | 192.168.0.5 | - | Root DNS server |
| dnsit | 192.168.0.1 | - | TLD DNS (.it) |
| dnsnet | 192.168.0.2 | - | TLD DNS (.net) |
| dnsuni | 192.168.0.11 | dnsuni.uniroma3.it | Authoritative DNS (uniroma3.it) |
| dnsstart | 192.168.0.22 | - | Authoritative DNS (startup.net) |
| localuni | 192.168.0.110 | localuni.uniroma3.it | Local DNS (.it zone) |
| localstart | 192.168.0.220 | - | Local DNS (.net zone) |
| pc1 | 192.168.0.111 | pc1.uniroma3.it | Test client |
| pc2 | 192.168.0.222 | pc2.startup.net | Test client |
| api | 192.168.0.112 | api.startup.net | Backend API service |
| frontend | 192.168.0.113 | frontend.startup.net | Frontend HTML service |
| llm | 192.168.0.114 | llm.startup.net | LLM streaming service |

---

## Getting Started

### Step 1: Start the Lab

Navigate to the lab directory and start all containers:

```bash
cd /tmp/reti-lab-kathara/lab4-dns-http
bash start-lab.sh
```

**Expected Output:**
```
Starting lab...
[INFO] Starting container: dnsroot
[INFO] Starting container: dnsit
[INFO] Starting container: dnsnet
...
[INFO] All containers started successfully
```

**Wait Time**: The LLM service may take 5-10 minutes to download the gemma2:2b model on first start.

### Step 2: Verify Services

Check that all containers are running:

```bash
kathara list
```

You should see all 12 containers in the "running" state.

### Step 3: Open Wireshark

1. Open your web browser
2. Navigate to: `http://localhost:3000`
3. Click on "eth1" interface
4. Click "Start Capturing"

**Tip**: Use the display filter box at the top to filter packets (e.g., `dns`, `http`, `tcp`).

### Step 4: Connect to pc1

Open a terminal to pc1:

```bash
kathara connect pc1
```

You're now inside the pc1 container. All subsequent commands in this tutorial assume you're in pc1 unless stated otherwise.

---

## Part 1: Basic DNS Resolution

### Exercise 1.1: Simple DNS Query

Let's resolve a local hostname using DNS.

**Command:**
```bash
dig A pc1.uniroma3.it
```

**Expected Output:**
```
; <<>> DiG 9.x.x <<>> A pc1.uniroma3.it
;; QUESTION SECTION:
;pc1.uniroma3.it.        IN    A

;; ANSWER SECTION:
pc1.uniroma3.it.  60000  IN    A    192.168.0.111

;; Query time: 2 msec
;; SERVER: 192.168.0.110#53(192.168.0.110)
```

**What Happened?**
1. pc1 sent a DNS query to its configured DNS server (localuni at 192.168.0.110)
2. localuni returned the IP address from its zone file
3. The response shows pc1.uniroma3.it → 192.168.0.111

### Exercise 1.2: Wireshark Analysis

Switch to Wireshark and apply filter: `dns`

**Observe:**
- Query packet: pc1 → localuni (UDP port 53)
- Response packet: localuni → pc1
- DNS query type: A (IPv4 address)
- DNS response: Answer RR with IP address

**Key Fields to Examine:**
- **Transaction ID**: Matches query and response
- **Flags**: 0x0100 (standard query), 0x8180 (response)
- **Questions**: 1
- **Answer RRs**: 1
- **TTL**: 60000 seconds

---

## Part 2: Hierarchical DNS

### Exercise 2.1: Cross-Domain Resolution

Now let's query a domain in a different zone to see hierarchical resolution.

**Command:**
```bash
dig A pc2.startup.net
```

**Expected Output:**
```
;; ANSWER SECTION:
pc2.startup.net.  60000  IN    A    192.168.0.222
```

**What Happened?**
1. pc1 → localuni: "What is pc2.startup.net?"
2. localuni → dnsroot: "Who handles .net?"
3. dnsroot → localuni: "Ask dnsnet at 192.168.0.2"
4. localuni → dnsnet: "Who handles startup.net?"
5. dnsnet → localuni: "Ask dnsstart at 192.168.0.22"
6. localuni → dnsstart: "What is pc2.startup.net?"
7. dnsstart → localuni: "192.168.0.222"
8. localuni → pc1: "192.168.0.222"

### Exercise 2.2: Trace DNS Resolution

Use `dig +trace` to see the full resolution path:

```bash
dig +trace A pc2.startup.net
```

**Expected Output:**
```
.            60000  IN  NS  dnsroot.
dnsroot.     60000  IN  A   192.168.0.5
net.         60000  IN  NS  dnsnet.net.
dnsnet.net.  60000  IN  A   192.168.0.2
startup.net. 60000  IN  NS  dnsstart.startup.net.
dnsstart.startup.net. 60000 IN A 192.168.0.22
pc2.startup.net. 60000 IN  A   192.168.0.222
```

This shows each step of the delegation chain!

### Exercise 2.3: Wireshark - Full Resolution

In Wireshark, filter: `dns`

Count the number of DNS query/response pairs. You should see multiple exchanges:
1. Query to root for .net delegation
2. Query to .net for startup.net delegation
3. Query to startup.net for pc2 address

**Challenge**: Can you identify the NS (Name Server) records in the responses?

---

## Part 3: HTTP Services

### Exercise 3.1: Backend API - Visitor Counter

First, resolve the API service:

```bash
dig A api.startup.net
```

**Expected Output:**
```
api.startup.net.  60000  IN  A  192.168.0.112
```

Now make an HTTP request:

```bash
curl http://api.startup.net/visitors
```

**Expected Output:**
```json
{"visitors": 1}
```

Make the request again:
```bash
curl http://api.startup.net/visitors
```

**Expected Output:**
```json
{"visitors": 2}
```

The counter increments with each request!

### Exercise 3.2: Wireshark - HTTP Analysis

In Wireshark, filter: `http`

**Observe:**
1. **HTTP Request** (pc1 → api):
   - Method: GET
   - URI: /visitors
   - Host header: api.startup.net

2. **HTTP Response** (api → pc1):
   - Status: 200 OK
   - Content-Type: application/json
   - Body: {"visitors": X}

**Expand the HTTP packet:**
- Right-click → Follow → HTTP Stream
- See the complete request/response exchange

### Exercise 3.3: Frontend Service

The frontend queries the backend via DNS and returns HTML:

```bash
curl http://frontend.startup.net/
```

**Expected Output:**
```html
<!DOCTYPE html>
<html>
...
<h1>We had 3 visitors!</h1>
...
</html>
```

### Exercise 3.4: Wireshark - Service Communication

Filter: `http or dns`

**Observe the sequence:**
1. **DNS Query**: pc1 → localuni for frontend.startup.net
2. **DNS Response**: localuni → pc1 (192.168.0.113)
3. **HTTP Request**: pc1 → frontend
4. **DNS Query**: frontend → localuni for api.startup.net (!)
5. **DNS Response**: localuni → frontend (192.168.0.112)
6. **HTTP Request**: frontend → api
7. **HTTP Response**: api → frontend
8. **HTTP Response**: frontend → pc1

This shows **service-to-service communication via DNS**!

---

## Part 4: TCP Behavior

### Exercise 4.1: TCP Three-Way Handshake

Filter in Wireshark: `tcp and ip.addr == 192.168.0.112`

Make any HTTP request:
```bash
curl http://api.startup.net/visitors
```

**Observe the TCP handshake:**
1. **SYN**: pc1 → api (Flags: S)
2. **SYN-ACK**: api → pc1 (Flags: S, A)
3. **ACK**: pc1 → api (Flags: A)

Connection established! Then:
4. **PSH, ACK**: pc1 → api (HTTP request data)
5. **ACK**: api → pc1 (acknowledgment)
6. **PSH, ACK**: api → pc1 (HTTP response data)
7. **ACK**: pc1 → api (acknowledgment)
8. **FIN, ACK**: Connection termination

### Exercise 4.2: Large Payload - Multi-Packet

Request a large payload to see TCP segmentation:

```bash
curl http://api.startup.net/payload?chars=100000
```

**In Wireshark**, filter: `tcp.stream eq X` (use the stream number from your request)

**Observe:**
- Multiple TCP packets carrying the response
- Each packet has a **sequence number** and **acknowledgment number**
- **TCP window size** controls flow
- Some packets may show **[TCP segment of a reassembled PDU]**

**Key Concepts:**
- **MSS (Maximum Segment Size)**: Typically 1460 bytes
- **Sequence Numbers**: Track byte position in stream
- **Acknowledgments**: Confirm receipt of data

### Exercise 4.3: TCP Timeout

Test what happens when a server delays:

```bash
curl http://api.startup.net/delay?seconds=5
```

The response takes 5 seconds. Watch in Wireshark:

**Observe:**
- TCP connection stays open
- No data flows during the delay
- Eventually response arrives
- Connection closes normally

Now try a very long delay:
```bash
curl --max-time 3 http://api.startup.net/delay?seconds=30
```

curl times out after 3 seconds!

**In Wireshark:**
- Connection established
- No response received
- pc1 sends FIN to close connection
- **This is a client-side timeout**

---

## Part 5: Streaming Protocols

### Exercise 5.1: LLM Streaming Response

The LLM service streams responses token-by-token.

**Command** (note the `-N` flag to disable buffering):
```bash
curl -N 'http://llm.startup.net/ask?q=What is DNS?'
```

**Expected Output** (appears gradually):
```
DNS stands for Domain Name System. It's a hierarchical...
```

The response appears progressively, not all at once!

### Exercise 5.2: Wireshark - Chunked Transfer Encoding

Filter: `http.request.uri contains "ask"`

**Observe the HTTP response:**

1. Find the HTTP response packet
2. Look at the headers:
   ```
   Transfer-Encoding: chunked
   Cache-Control: no-cache
   ```

3. The response body comes in **multiple packets**, each containing a chunk of the response

**Expand HTTP packets:**
- Each chunk starts with a size (in hex)
- Followed by the chunk data
- Final chunk has size 0

**Key Concepts:**
- **Chunked Transfer Encoding**: Data sent in pieces without knowing total size upfront
- **Streaming**: Server sends data as it's generated
- **No Content-Length header**: Total size unknown

### Exercise 5.3: Compare Streaming vs. Non-Streaming

**Non-streaming (regular API):**
```bash
time curl http://api.startup.net/visitors
```
Response arrives all at once after processing completes.

**Streaming (LLM):**
```bash
time curl -N 'http://llm.startup.net/ask?q=Hi'
```
Response arrives progressively as tokens are generated.

**In Wireshark:**
- Non-streaming: Single HTTP response packet (or few packets if large)
- Streaming: Many HTTP packets over time

---

## Advanced Topics

### DNS Zone File Structure

Let's examine how DNS zones are configured.

**File**: `dnsuni/etc/bind/db.it.uniroma3`

```bash
# On your host machine, not in container
cat dnsuni/etc/bind/db.it.uniroma3
```

**Content:**
```
$TTL    60000
@               IN      SOA     dnsuni.uniroma3.it.    root.dnsuni.uniroma3.it. (
                        2006031202 ; serial
                        28 ; refresh
                        14 ; retry
                        3600000 ; expire
                        0 ; negative cache ttl
                        )

@                       IN  NS  dnsuni.uniroma3.it.
dnsuni.uniroma3.it.     IN  A   192.168.0.11

pc1.uniroma3.it.        IN  A   192.168.0.111
localuni.uniroma3.it.   IN  A   192.168.0.110

; Service nodes
api.startup.net.        IN  A   192.168.0.112
frontend.startup.net.   IN  A   192.168.0.113
llm.startup.net.        IN  A   192.168.0.114
```

**Explanation:**
- **$TTL**: Time-To-Live for records (60000 seconds)
- **SOA**: Start of Authority (authoritative DNS server info)
- **NS**: Name Server record (who is authoritative)
- **A**: Address record (hostname → IPv4)
- **Serial**: Zone version (increment when making changes)

### Kathara Startup Files

Kathara uses `.startup` files to configure containers on boot.

**File**: `api.startup`

```bash
ip address add 192.168.0.112/24 dev eth0

apt-get update
apt-get install -y python3 python3-pip

pip3 install fastapi uvicorn --break-system-packages

cd /hostlab/api
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 80 &
```

**Explanation:**
1. Configure network interface with IP
2. Install system packages
3. Install Python dependencies
4. Start the FastAPI application on port 80

### Pre-built Docker Images

The service containers use **custom pre-built Docker images** instead of the base `kathara/base` image:

**Images:**
- `dns-lab/api` - Backend API with Python + FastAPI pre-installed
- `dns-lab/frontend` - Frontend with Python + FastAPI + httpx pre-installed
- `dns-lab/llm` - LLM service with Python + FastAPI + Ollama + gemma3:270m model pre-installed

**How it works:**
1. Before first lab use, run `bash build-images.sh` (takes ~15-20 minutes)
2. Docker builds images with all dependencies and downloads LLM model
3. Images are cached locally on your machine
4. Lab startup uses pre-built images (starts in ~10 seconds)

**Lab.conf configuration:**
```
api[0]="A"                  # Internal network interface
api[image]="dns-lab/api"    # Custom pre-built image
```

**Benefits:**
- ✅ **Fast startup**: No package installation at runtime
- ✅ **Offline operation**: No internet needed after initial build
- ✅ **Isolated network**: Pure lab environment without external dependencies
- ✅ **Reproducible**: Same image works identically everywhere
- ✅ **Classroom ready**: Quick startup for demos and exercises

The internal network (collision domain A) is completely isolated. Internet is only required when building the Docker images, not during lab execution.

### HTTP Headers Deep Dive

Make a request and examine all headers:

```bash
curl -v http://api.startup.net/visitors
```

**Request Headers:**
```
GET /visitors HTTP/1.1
Host: api.startup.net
User-Agent: curl/7.x.x
Accept: */*
```

**Response Headers:**
```
HTTP/1.1 200 OK
content-type: application/json
content-length: 15
date: ...
server: uvicorn
```

**In Wireshark:**
Right-click HTTP packet → Follow → HTTP Stream

See the complete, unencrypted HTTP conversation!

---

## Troubleshooting

### DNS Resolution Fails

**Symptom:**
```bash
dig A api.startup.net
# Returns NXDOMAIN (non-existent domain)
```

**Diagnosis:**
1. Check DNS server is running:
   ```bash
   # On host
   kathara exec dnsuni -- systemctl status named
   ```

2. Verify zone file exists:
   ```bash
   kathara exec dnsuni -- cat /etc/bind/db.it.uniroma3
   ```

3. Check DNS server logs:
   ```bash
   kathara exec dnsuni -- tail -f /var/log/syslog
   ```

**Solution:**
Restart the DNS service:
```bash
kathara exec dnsuni -- systemctl restart named
```

### Service Not Responding

**Symptom:**
```bash
curl http://api.startup.net/visitors
# Hangs or connection refused
```

**Diagnosis:**
1. Verify DNS resolution works:
   ```bash
   dig A api.startup.net
   ```

2. Check if service is running:
   ```bash
   kathara exec api -- ps aux | grep uvicorn
   ```

3. Check service logs:
   ```bash
   kathara exec api -- journalctl -f
   ```

4. Test direct IP connection:
   ```bash
   curl http://192.168.0.112/visitors
   ```

**Solution:**
Restart the service:
```bash
kathara exec api -- pkill -f uvicorn
kathara exec api -- bash /hostlab/api.startup
```

### Wireshark Shows No Packets

**Symptom:**
Wireshark interface shows no captured packets

**Diagnosis:**
1. Verify you're capturing on the correct interface (eth1)
2. Check if containers are communicating
3. Ensure capture filter is not too restrictive

**Solution:**
1. Stop capture
2. Select "eth1" interface
3. Start capture without any filter
4. Generate traffic from pc1

### LLM Service Not Streaming

**Symptom:**
curl shows response all at once, not streaming

**Diagnosis:**
- Forgot `-N` flag in curl command

**Solution:**
```bash
curl -N 'http://llm.startup.net/ask?q=test'
```

The `-N` flag disables buffering, allowing you to see streaming output.

---

## Summary

Congratulations! You've completed the DNS lab tutorial. You've learned:

- ✅ How DNS resolution works hierarchically
- ✅ How to analyze DNS queries in Wireshark
- ✅ How HTTP requests and responses work
- ✅ How TCP establishes connections and transfers data
- ✅ How streaming protocols differ from regular HTTP
- ✅ How to use Wireshark for network analysis
- ✅ How to troubleshoot networking issues

### Next Steps

1. Complete the [WIRESHARK_EXERCISES.md](WIRESHARK_EXERCISES.md) for hands-on practice
2. Review the [SERVICES_GUIDE.md](SERVICES_GUIDE.md) for API details
3. Experiment with modifying zone files
4. Try adding your own services to the network

### Further Reading

- DNS RFC 1035: https://www.rfc-editor.org/rfc/rfc1035
- HTTP/1.1 RFC 7230: https://www.rfc-editor.org/rfc/rfc7230
- TCP RFC 793: https://www.rfc-editor.org/rfc/rfc793
- Wireshark User Guide: https://www.wireshark.org/docs/

---

**Happy Learning!** 🚀
