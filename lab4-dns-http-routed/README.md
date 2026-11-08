# Networking - DNS Lab with Routers

This lab demonstrates a hierarchical DNS system separated into different collision domains connected by routers. The three main DNS domains (ROOT, .it, .net) are each in their own network, connected via a triangle of routers.

## Network Topology

```
        Rete ROOT                Rete IT                 Rete NET
      192.168.0.0/24          192.168.1.0/24          192.168.2.0/24
           |                      |                       |
       [dnsroot]         [dnsit] [dnsuni]        [dnsnet] [dnsstart]
           |             [localuni] [pc1]        [localstart] [pc2]
           |                      |              [api] [frontend] [llm]
           |                      |                       |
        [R_ROOT]---------------[R_IT]------------------[R_NET]
             \                                          /
              \                                        /
               +--------------------------------------+
```

### Networks

| Network | CIDR            | Description         |
| ------- | --------------- | ------------------- |
| ROOT    | 192.168.0.0/24  | Root DNS domain     |
| IT      | 192.168.1.0/24  | .it TLD domain      |
| NET     | 192.168.2.0/24  | .net TLD domain     |
| LINK_RI | 192.168.10.0/24 | R_ROOT ↔ R_IT link  |
| LINK_IN | 192.168.20.0/24 | R_IT ↔ R_NET link   |
| LINK_RN | 192.168.30.0/24 | R_ROOT ↔ R_NET link |

### Routers

| Router | eth0                 | eth1                   | eth2                   |
| ------ | -------------------- | ---------------------- | ---------------------- |
| R_ROOT | 192.168.0.100 (ROOT) | 192.168.10.1 (LINK_RI) | 192.168.30.1 (LINK_RN) |
| R_IT   | 192.168.1.100 (IT)   | 192.168.10.2 (LINK_RI) | 192.168.20.1 (LINK_IN) |
| R_NET  | 192.168.2.100 (NET)  | 192.168.20.2 (LINK_IN) | 192.168.30.2 (LINK_RN) |

### DNS Servers

| Server     | IP            | Network | Description                       |
| ---------- | ------------- | ------- | --------------------------------- |
| dnsroot    | 192.168.0.5   | ROOT    | Root DNS server (.)               |
| dnsit      | 192.168.1.1   | IT      | TLD DNS for .it                   |
| dnsuni     | 192.168.1.11  | IT      | Authoritative DNS for uniroma3.it |
| localuni   | 192.168.1.110 | IT      | Local DNS server for .it zone     |
| dnsnet     | 192.168.2.2   | NET     | TLD DNS for .net                  |
| dnsstart   | 192.168.2.22  | NET     | Authoritative DNS for startup.net |
| localstart | 192.168.2.220 | NET     | Local DNS server for .net zone    |

### Client Machines

| Client | IP            | Network |
| ------ | ------------- | ------- |
| pc1    | 192.168.1.111 | IT      |
| pc2    | 192.168.2.222 | NET     |

### Service Nodes

| Service  | IP            | Network | DNS Name             |
| -------- | ------------- | ------- | -------------------- |
| api      | 192.168.2.112 | NET     | api.startup.net      |
| frontend | 192.168.2.113 | NET     | frontend.startup.net |
| llm      | 192.168.2.114 | NET     | llm.startup.net      |

## Quick Start

### 1. Build Docker Images (First Time Only)

```bash
bash build-images.sh
```

### 2. Start the Lab

```bash
bash start-lab.sh
```

### 3. Open Wireshark

Open your browser to `localhost:3000` and start capturing packets.

### 4. Test Routing

Connect to pc1 (in IT network) and test connectivity to NET network:

```bash
kathara connect pc1

# Ping pc2 in NET network (crosses R_IT and R_NET)
ping 192.168.2.222

# Ping dnsroot in ROOT network (crosses R_IT and R_ROOT)
ping 192.168.0.5

# Trace the route to see hops
traceroute 192.168.2.222
```

### 5. Test DNS Resolution

From pc1, resolve services across networks:

```bash
# Resolve API service (in NET network)
dig A api.startup.net

# The DNS query will traverse:
# pc1 -> R_IT -> R_ROOT (dnsroot) -> R_IT -> R_NET (dnsnet -> dnsstart)
```

### 6. Test HTTP Services

```bash
# From pc1, access services in NET network
curl http://api.startup.net/visitors
curl http://frontend.startup.net/
```

## Learning Objectives

1. **Routing**: Understand how packets traverse routers between networks
2. **Static Routes**: See how routers are configured to forward packets
3. **DNS across networks**: Observe DNS resolution crossing network boundaries
4. **Default Gateway**: Understand how clients use gateways to reach remote networks

## Router Configuration

Each router has static routes configured. For example, R_ROOT:

```bash
# Routes to reach other networks
ip route add 192.168.1.0/24 via 192.168.10.2   # IT network via R_IT
ip route add 192.168.2.0/24 via 192.168.30.2   # NET network via R_NET
ip route add 192.168.20.0/24 via 192.168.10.2  # LINK_IN via R_IT
```

## Useful Commands

```bash
# View routing table on any node
route -n

# View routing table (alternative)
route -n

# Trace route to destination
traceroute <ip>

# Connect to a router
kathara connect r_root
kathara connect r_it
kathara connect r_net
```

---

## Differences from dns_http Lab

This lab (`dns_http_routed`) extends the original `dns_http` lab by separating machines into different collision domains connected by routers.

### Topology Comparison

| Aspect                | dns_http               | dns_http_routed                     |
| --------------------- | ---------------------- | ----------------------------------- |
| **Networks**          | 1 (all on network "A") | 6 (ROOT, IT, NET + 3 link networks) |
| **Routers**           | None                   | 3 (R_ROOT, R_IT, R_NET)             |
| **Collision domains** | 1                      | 6                                   |

### IP Address Changes

The fourth octet is preserved to maintain familiarity. Only the third octet changes based on the network:

| Machine    | dns_http      | dns_http_routed   | Network |
| ---------- | ------------- | ----------------- | ------- |
| dnsroot    | 192.168.0.5   | 192.168.**0**.5   | ROOT    |
| dnsit      | 192.168.0.1   | 192.168.**1**.1   | IT      |
| dnsuni     | 192.168.0.11  | 192.168.**1**.11  | IT      |
| localuni   | 192.168.0.110 | 192.168.**1**.110 | IT      |
| pc1        | 192.168.0.111 | 192.168.**1**.111 | IT      |
| dnsnet     | 192.168.0.2   | 192.168.**2**.2   | NET     |
| dnsstart   | 192.168.0.22  | 192.168.**2**.22  | NET     |
| localstart | 192.168.0.220 | 192.168.**2**.220 | NET     |
| pc2        | 192.168.0.222 | 192.168.**2**.222 | NET     |
| api        | 192.168.0.112 | 192.168.**2**.112 | NET     |
| frontend   | 192.168.0.113 | 192.168.**2**.113 | NET     |
| llm        | 192.168.0.114 | 192.168.**2**.114 | NET     |

### New Files

Files added in `dns_http_routed` that don't exist in `dns_http`:

| File             | Purpose                                         |
| ---------------- | ----------------------------------------------- |
| `r_root.startup` | Router ROOT configuration (IPs + static routes) |
| `r_it.startup`   | Router IT configuration (IPs + static routes)   |
| `r_net.startup`  | Router NET configuration (IPs + static routes)  |

### Modified Files

| File                            | Change                                                             |
| ------------------------------- | ------------------------------------------------------------------ |
| `lab.conf`                      | Added 3 routers, changed collision domains from "A" to ROOT/IT/NET |
| `*.startup`                     | Added default gateway (`route add default gw ...`)                 |
| `*/etc/bind/db.*`               | Updated IP addresses                                               |
| `*/etc/bind/named.conf.options` | Changed `allow-recursion` to `192.168.0.0/16`                      |
| `*/etc/resolv.conf`             | Updated nameserver IPs                                             |

### Key Configuration Differences

#### 1. lab.conf - Collision Domains

**dns_http:**

```
pc1[0]="A"
dnsroot[0]="A"
# All machines on same network "A"
```

**dns_http_routed:**

```
pc1[0]="IT"
dnsroot[0]="ROOT"
dnsnet[0]="NET"
r_root[0]="ROOT"
r_root[1]="LINK_RI"
r_root[2]="LINK_RN"
```

#### 2. Startup Files - Default Gateway

**dns_http (pc1.startup):**

```bash
ip address add 192.168.0.111/24 dev eth0
ip link set eth0 up
# No gateway needed - all on same network
```

**dns_http_routed (pc1.startup):**

```bash
ip address add 192.168.1.111/24 dev eth0
ip link set eth0 up
route add default gw 192.168.1.100 dev eth0  # Gateway to R_IT
```

#### 3. Router Configuration (new)

Each router needs:

- Multiple interfaces (one per connected network)
- Static routes to reach non-adjacent networks

**r_root.startup:**

```bash
ip addr add 192.168.0.100/24 dev eth0   # ROOT network
ip addr add 192.168.10.1/24 dev eth1    # Link to R_IT
ip addr add 192.168.30.1/24 dev eth2    # Link to R_NET

# Static routes
ip route add 192.168.1.0/24 via 192.168.10.2   # IT via R_IT
ip route add 192.168.2.0/24 via 192.168.30.2   # NET via R_NET
ip route add 192.168.20.0/24 via 192.168.10.2  # LINK_IN via R_IT
```

### Wireshark Differences

| Aspect                 | dns_http                     | dns_http_routed               |
| ---------------------- | ---------------------------- | ----------------------------- |
| **Interfaces**         | 1 (eth1)                     | 6 (eth0-eth5)                 |
| **Configuration**      | Static in lab.conf           | Dynamic via `kathara lconfig` |
| **Traffic visibility** | All traffic on one interface | Choose interface per network  |

**Wireshark interfaces in dns_http_routed:**

- eth1: ROOT network
- eth2: IT network
- eth3: NET network
- eth4: LINK_RI (R_ROOT ↔ R_IT)
- eth5: LINK_IN (R_IT ↔ R_NET)
- eth6: LINK_RN (R_ROOT ↔ R_NET)

### What You Can Observe

With routers, you can now observe:

1. **Packet routing**: Use `traceroute` to see hops between networks
2. **TTL decrement**: Watch TTL decrease as packets cross routers
3. **Multiple paths**: Traffic can take different routes (e.g., IT→NET can go via R_IT→R_NET or R_IT→R_ROOT→R_NET)
4. **ARP per network**: Each network has its own ARP table
5. **DNS across boundaries**: DNS queries traverse multiple routers to reach authoritative servers
