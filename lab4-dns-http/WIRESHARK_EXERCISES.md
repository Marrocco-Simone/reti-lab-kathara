# Wireshark Exercises: DNS Lab

This document contains hands-on exercises for analyzing network traffic captured in the DNS lab. Each exercise includes the question, detailed steps to find the answer, and the solution.

## Table of Contents

1. [DNS Analysis](#dns-analysis)
2. [HTTP Protocol](#http-protocol)
3. [TCP Behavior](#tcp-behavior)
4. [Streaming Protocols](#streaming-protocols)
5. [Advanced Analysis](#advanced-analysis)

---

## DNS Analysis

<details>
<summary><strong>Exercise 1: What is the IP address of api.startup.net?</strong></summary>

### Steps

1. Start Wireshark capture on eth1
2. From pc1, run: `dig A api.startup.net`
3. In Wireshark, apply filter: `dns.qry.name == "api.startup.net"`
4. Look at the DNS response packet
5. Expand: Domain Name System (response) → Answers
6. Find the A record

### Answer

**192.168.0.212**

The DNS response contains an A (Address) record mapping api.startup.net to 192.168.0.212.

</details>

<details>
<summary><strong>Exercise 2: How many DNS queries are required to resolve pc2.startup.net from pc1?</strong></summary>

### Steps

1. Clear Wireshark capture
2. From pc1, run: `dig A pc2.startup.net`
3. Apply filter: `dns`
4. Count query packets (look for "Standard query" in Info column)
5. Trace the delegation chain:
   - Query for root (.)
   - Query for .net TLD
   - Query for startup.net domain
   - Query for pc2.startup.net host

### Answer

**4 DNS queries** (or 3 if local DNS has cached the delegation)

1. Query to root server for .net
2. Query to .net TLD for startup.net
3. Query to startup.net authoritative for pc2
4. (Possibly) Additional queries for NS records

Note: The exact number may vary depending on caching.

</details>

<details>
<summary><strong>Exercise 3: What is the DNS transaction ID for the query api.startup.net?</strong></summary>

### Steps

1. Capture traffic while running: `dig A api.startup.net`
2. Filter: `dns.qry.name == "api.startup.net"`
3. Select the query packet (not the response)
4. Expand: Domain Name System (query)
5. Look for "Transaction ID"

### Answer

**Variable** - The transaction ID changes for each query, typically a 16-bit random number (e.g., 0x1a2b, 0x4f3c).

The same transaction ID appears in both the query and the matching response.

</details>

<details>
<summary><strong>Exercise 4: What DNS server does pc1 use for queries?</strong></summary>

### Steps

1. Capture DNS traffic
2. From pc1, run: `dig A api.startup.net`
3. Filter: `dns`
4. Look at the destination IP of the DNS query packet
5. Cross-reference with the IP table (or run `dig` and check the SERVER line)

### Answer

**192.168.0.110 (localuni.uniroma3.it)**

pc1 is configured to use localuni as its DNS resolver.

</details>

<details>
<summary><strong>Exercise 5: What is the TTL (Time To Live) for the A record of api.startup.net?</strong></summary>

### Steps

1. Filter: `dns.qry.name == "api.startup.net"`
2. Select the DNS response packet
3. Expand: Answers → api.startup.net: type A, class IN
4. Look for "Time to live"

### Answer

**60000 seconds** (approximately 16.7 hours)

This is defined in the zone file as `$TTL 60000`.

</details>

---

## HTTP Protocol

<details>
<summary><strong>Exercise 6: What HTTP method is used to request /visitors?</strong></summary>

### Steps

1. From pc1, run: `curl http://api.startup.net/visitors`
2. Filter: `http.request.uri == "/visitors"`
3. Select the HTTP request packet
4. Look at: Hypertext Transfer Protocol → Request Method

### Answer

**GET**

The client uses the HTTP GET method to retrieve the visitor count.

</details>

<details>
<summary><strong>Exercise 7: What is the User-Agent header in curl requests?</strong></summary>

### Steps

1. Make a request: `curl http://api.startup.net/visitors`
2. Filter: `http.request`
3. Select the HTTP request packet
4. Expand: Hypertext Transfer Protocol → User-Agent

### Answer

**curl/7.x.x** (version may vary)

The User-Agent identifies the client software making the request.

</details>

<details>
<summary><strong>Exercise 8: What is the Content-Type of the API response?</strong></summary>

### Steps

1. Make a request: `curl http://api.startup.net/visitors`
2. Filter: `http.response`
3. Select the HTTP response packet
4. Expand: Hypertext Transfer Protocol → Content-Type

### Answer

**application/json**

The API returns JSON-formatted data.

</details>

<details>
<summary><strong>Exercise 9: How many HTTP requests does the frontend make to render the page?</strong></summary>

### Steps

1. Clear capture
2. Run: `curl http://frontend.startup.net/`
3. Filter: `http.request`
4. Count packets originating from frontend (192.168.0.213)

### Answer

**2 HTTP requests**

1. pc1 → frontend: GET /
2. frontend → api: GET /visitors

The frontend makes a second request to the backend API to fetch visitor count.

</details>

<details>
<summary><strong>Exercise 10: What HTTP status code does /visitors return?</strong></summary>

### Steps

1. Request: `curl http://api.startup.net/visitors`
2. Filter: `http.response`
3. Look at: Hypertext Transfer Protocol → Status Code

### Answer

**200 OK**

Indicates successful request and response.

</details>

---

## TCP Behavior

<details>
<summary><strong>Exercise 11: What are the three TCP flags used in the connection handshake?</strong></summary>

### Steps

1. Make request: `curl http://api.startup.net/visitors`
2. Filter: `tcp and ip.addr == 192.168.0.212`
3. Look at the first three TCP packets
4. Examine the Flags field in each packet:
   - Packet 1: Flags
   - Packet 2: Flags
   - Packet 3: Flags

### Answer

**SYN, SYN-ACK, ACK**

1. **SYN**: Client initiates connection
2. **SYN-ACK**: Server acknowledges and responds
3. **ACK**: Client acknowledges server's response

This is the TCP three-way handshake.

</details>

<details>
<summary><strong>Exercise 12: What is the TCP window size in the initial SYN packet?</strong></summary>

### Steps

1. Capture HTTP request
2. Filter: `tcp.flags.syn == 1 and tcp.flags.ack == 0`
3. Select the SYN packet
4. Expand: Transmission Control Protocol → Window size value

### Answer

**Variable** - Typically **64240** or **65535** bytes (or similar)

The window size indicates how much data the receiver can accept before needing an acknowledgment.

</details>

<details>
<summary><strong>Exercise 13: How many TCP segments are needed to transfer a 100,000-character payload?</strong></summary>

### Steps

1. Request: `curl http://api.startup.net/payload?chars=100000`
2. Filter: `tcp.stream eq N` (replace N with your stream number)
3. Count packets with PSH flag or [TCP segment of a reassembled PDU]
4. Calculate: payload size / MSS ≈ number of packets

### Answer

**Approximately 69-70 TCP segments**

Calculation:
- Payload: ~100,000 bytes + HTTP headers (~200 bytes)
- MSS (Maximum Segment Size): typically 1460 bytes
- Segments: 100,200 / 1460 ≈ 69

Actual number may vary based on TCP options and segmentation.

</details>

<details>
<summary><strong>Exercise 14: What happens when you request /delay?seconds=30 with a 5-second timeout?</strong></summary>

### Steps

1. Run: `curl --max-time 5 http://api.startup.net/delay?seconds=30`
2. Capture the traffic
3. Filter: `tcp.stream eq N`
4. Observe the sequence:
   - SYN, SYN-ACK, ACK (connection established)
   - HTTP request sent
   - Long wait...
   - FIN or RST from client

### Answer

**Client sends FIN/RST to close connection**

After 5 seconds, curl times out and terminates the connection because the server hasn't responded. The client sends a FIN (finish) or RST (reset) packet to close the TCP connection.

</details>

<details>
<summary><strong>Exercise 15: What is the sequence number increment between consecutive TCP data packets?</strong></summary>

### Steps

1. Request large payload: `curl http://api.startup.net/payload?chars=50000`
2. Filter: `tcp.stream eq N and tcp.len > 0`
3. Select two consecutive data packets
4. Compare their sequence numbers
5. Calculate: SEQ(packet 2) - SEQ(packet 1)

### Answer

**Equal to the length of the previous packet's data** (typically 1460 bytes for full segments)

Example:
- Packet 1: SEQ=1, Len=1460 → Next expected SEQ = 1461
- Packet 2: SEQ=1461, Len=1460 → Next expected SEQ = 2921

Sequence numbers track byte position in the TCP stream.

</details>

---

## Streaming Protocols

<details>
<summary><strong>Exercise 16: What Transfer-Encoding does the LLM service use?</strong></summary>

### Steps

1. Request: `curl -N 'http://llm.startup.net/ask?q=test'`
2. Filter: `http.request.uri contains "ask"`
3. Find the HTTP response
4. Expand: Hypertext Transfer Protocol → Transfer-Encoding

### Answer

**chunked**

Chunked transfer encoding allows the server to send data in pieces without knowing the total content length upfront.

</details>

<details>
<summary><strong>Exercise 17: How many TCP packets contain the streaming response for a simple question?</strong></summary>

### Steps

1. Run: `curl -N 'http://llm.startup.net/ask?q=Hi'`
2. Filter: `http.response or tcp.stream eq N`
3. Count packets containing response data
4. Look for packets with [HTTP/1.1 200 OK] and subsequent data packets

### Answer

**Variable** - Typically **5-15 packets** depending on response length

The response is streamed token-by-token, with multiple TCP packets carrying chunks of the response as the LLM generates them.

</details>

<details>
<summary><strong>Exercise 18: Is there a Content-Length header in streaming responses?</strong></summary>

### Steps

1. Request: `curl -N 'http://llm.startup.net/ask?q=test'`
2. Find the HTTP response
3. Expand headers
4. Search for "Content-Length"

### Answer

**No**

Streaming responses use `Transfer-Encoding: chunked` instead of `Content-Length` because the total size is unknown when the response begins.

</details>

<details>
<summary><strong>Exercise 19: How does streaming differ from non-streaming in Wireshark?</strong></summary>

### Steps

1. **Non-streaming**: `curl http://api.startup.net/visitors`
2. **Streaming**: `curl -N 'http://llm.startup.net/ask?q=test'`
3. Compare:
   - Number of packets
   - Time between packets
   - Transfer-Encoding headers
   - Response arrival pattern

### Answer

**Non-streaming**:
- Single HTTP response packet (or few if large)
- All data arrives at once
- Content-Length header present
- Fast, immediate response

**Streaming**:
- Multiple HTTP packets over time
- Data arrives progressively
- Transfer-Encoding: chunked
- Responses arrive as generated (observable delay between chunks)

</details>

<details>
<summary><strong>Exercise 20: What cache-control header does the LLM service send?</strong></summary>

### Steps

1. Request: `curl -N 'http://llm.startup.net/ask?q=test'`
2. Find HTTP response
3. Look for: Cache-Control header

### Answer

**no-cache**

This prevents caching of AI-generated responses, ensuring fresh responses for each query.

</details>

---

## Advanced Analysis

<details>
<summary><strong>Exercise 21: What is the round-trip time (RTT) for the TCP handshake?</strong></summary>

### Steps

1. Make HTTP request
2. Filter: `tcp.flags.syn == 1`
3. Select the SYN packet
4. Note timestamp (T1)
5. Find the SYN-ACK response
6. Note timestamp (T2)
7. Calculate: RTT = (T2 - T1) × 2

### Answer

**Variable** - Typically **< 1 millisecond** in local network

For containers on the same host, RTT is very low (microseconds to milliseconds).

</details>

<details>
<summary><strong>Exercise 22: How many bytes of DNS overhead are used to resolve api.startup.net?</strong></summary>

### Steps

1. Clear capture
2. Run: `dig A api.startup.net`
3. Filter: `dns.qry.name == "api.startup.net"`
4. Select query packet → Look at "Length" field in packet details
5. Select response packet → Look at "Length" field
6. Add: Query length + Response length

### Answer

**Approximately 70-100 bytes total**

- Query: ~30-40 bytes (DNS header + question)
- Response: ~40-60 bytes (DNS header + answer)

Actual size varies based on additional records and flags.

</details>

<details>
<summary><strong>Exercise 23: What percentage of traffic is TCP vs. DNS vs. HTTP?</strong></summary>

### Steps

1. Capture all traffic for a full exercise session
2. Go to: Statistics → Protocol Hierarchy
3. Examine percentages for:
   - TCP
   - DNS (under UDP)
   - HTTP (under TCP)

### Answer

**Variable** - Typical distribution:
- **TCP**: 85-90% (includes HTTP and TCP overhead)
- **DNS**: 5-10% (UDP-based queries)
- **HTTP**: 70-80% (application data over TCP)

Depends on the mix of commands executed.

</details>

<details>
<summary><strong>Exercise 24: How can you identify DNS queries vs. responses?</strong></summary>

### Steps

1. Filter: `dns`
2. Look at the Info column
3. Observe patterns:
   - Queries: "Standard query"
   - Responses: "Standard query response"
4. Alternative: Check Flags field → QR bit (0=query, 1=response)

### Answer

**Check the Info column or Flags field**

- **Query**: Info shows "Standard query", Flags QR bit = 0
- **Response**: Info shows "Standard query response", Flags QR bit = 1

</details>

<details>
<summary><strong>Exercise 25: Using tshark, how do you extract all DNS query names?</strong></summary>

### Steps

1. Run commands to generate DNS traffic
2. On host machine, run:
   ```bash
   tshark -r capture.pcap -Y "dns.flags.response == 0" -T fields -e dns.qry.name
   ```
3. This extracts just the query names from DNS query packets

### Answer

**Command**:
```bash
tshark -r capture.pcap -Y "dns.flags.response == 0" -T fields -e dns.qry.name
```

**Output** (example):
```
api.startup.net
frontend.startup.net
llm.startup.net
pc2.startup.net
```

This shows all domain names queried during the capture.

</details>

---

## Bonus Challenges

<details>
<summary><strong>Challenge 1: Reconstruct the full HTTP conversation for /visitors</strong></summary>

### Steps

1. Capture: `curl http://api.startup.net/visitors`
2. Find the HTTP request packet
3. Right-click → Follow → HTTP Stream
4. Wireshark shows the complete conversation:
   - Request headers and body
   - Response headers and body

### Answer

**Request**:
```
GET /visitors HTTP/1.1
Host: api.startup.net
User-Agent: curl/7.x.x
Accept: */*

```

**Response**:
```
HTTP/1.1 200 OK
content-type: application/json
content-length: 15
...

{"visitors":1}
```

</details>

<details>
<summary><strong>Challenge 2: Calculate the efficiency ratio of useful data vs. total bytes</strong></summary>

### Steps

1. Make request: `curl http://api.startup.net/visitors`
2. Find HTTP response
3. Note:
   - Useful data (JSON payload): ~15 bytes
   - Total packet size: ~200+ bytes (Ethernet + IP + TCP + HTTP headers + data)
4. Calculate: (useful data / total bytes) × 100%

### Answer

**Approximately 7-10% efficiency**

Most bytes are protocol overhead:
- Ethernet header: 14 bytes
- IP header: 20 bytes
- TCP header: 20+ bytes
- HTTP headers: ~100-150 bytes
- Actual data: 15 bytes

Total: ~220 bytes for 15 bytes of data = 6.8% efficiency

This shows why HTTP/2 and HTTP/3 were developed to reduce overhead!

</details>

---

## Summary

You've completed the Wireshark exercises! You've learned to:

- ✅ Analyze DNS queries and responses
- ✅ Understand HTTP request/response structure
- ✅ Examine TCP connection lifecycle
- ✅ Identify streaming vs. non-streaming protocols
- ✅ Calculate protocol overhead and efficiency
- ✅ Use Wireshark filters effectively
- ✅ Extract data with tshark

### Recommended Display Filters

Here are useful Wireshark filters for this lab:

```
dns                              # All DNS traffic
dns.qry.name == "api.startup.net"  # Specific domain query
http                             # All HTTP traffic
http.request.method == "GET"     # HTTP GET requests
http.response.code == 200        # Successful HTTP responses
tcp.flags.syn == 1               # TCP SYN packets (connection starts)
tcp.stream eq 0                  # Follow specific TCP stream
ip.addr == 192.168.0.212         # Traffic to/from specific IP
tcp.analysis.retransmission      # TCP retransmissions (errors)
http.transfer_encoding == "chunked"  # Streaming responses
```

### Next Steps

- Experiment with more complex queries
- Try modifying zone files and observing changes
- Capture and analyze traffic from the frontend → backend communication
- Explore Statistics → Conversations to see all connections

**Happy packet hunting!** 🔍
