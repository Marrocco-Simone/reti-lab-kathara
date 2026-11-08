---
marp: true
theme: gaia
_class: lead
paginate: true
author: Reti - Laboratorio 2026/2027
description: Reti - Laboratorio 2026/2027
lang: italian
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')

title: DNS and HTTP with routers
---

# DNS e HTTP con router

---

## Setup

```bash
cd /tmp
git clone https://github.com/Marrocco-Simone/reti-lab-kathara
cd reti-lab-kathara/lab5-dns-http-routed
./build-images.sh
```

**Attenzione**: `/tmp` viene cancellata allo spegnimento del PC. Copiate altrove i file che modificate!

---

## Esercizio: Separare i Domini DNS

Attualmente tutti i nodi sono nella stessa rete "A".

Vogliamo separare i tre domini principali:

- **Dominio ROOT** (.): dnsroot
- **Dominio .it**: dnsit, dnsuni, localuni, pc1
- **Dominio .net**: dnsnet, dnsstart, localstart, pc2, api, frontend, llm

---

## Topologia Target

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

I tre router sono tutti connessi tra loro (topologia a triangolo).

---

## I Tre Router

| Router | eth0                  | eth1           | eth2           |
| ------ | --------------------- | -------------- | -------------- |
| R_ROOT | ROOT (192.168.0.0/24) | Link a R_IT    | Link a R_NET   |
| R_IT   | IT (192.168.1.0/24)   | Link da R_ROOT | Link a R_NET   |
| R_NET  | NET (192.168.2.0/24)  | Link da R_IT   | Link da R_ROOT |

---

## I Tre Router

Reti di collegamento tra i router:

- **LINK_RI** (R_ROOT ↔ R_IT): 192.168.10.0/24
- **LINK_IN** (R_IT ↔ R_NET): 192.168.20.0/24
- **LINK_RN** (R_ROOT ↔ R_NET): 192.168.30.0/24

---

### Modifiche a lab.conf (1/2)

```conf
# Rete ROOT - dominio radice
dnsroot[0]="ROOT"

# Rete IT - dominio .it
dnsit[0]="IT"
dnsuni[0]="IT"
localuni[0]="IT"
pc1[0]="IT"

# Rete NET - dominio .net
dnsnet[0]="NET"
dnsstart[0]="NET"
localstart[0]="NET"
pc2[0]="NET"
api[0]="NET"
frontend[0]="NET"
llm[0]="NET"
```

---

### Modifiche a lab.conf (2/2)

```conf
# Router ROOT: connette ROOT, R_IT e R_NET
r_root[0]="ROOT"       # eth0 -> rete ROOT
r_root[1]="LINK_RI"    # eth1 -> link verso R_IT
r_root[2]="LINK_RN"    # eth2 -> link verso R_NET

# Router IT: connette IT, R_ROOT e R_NET
r_it[0]="IT"           # eth0 -> rete IT
r_it[1]="LINK_RI"      # eth1 -> link da R_ROOT
r_it[2]="LINK_IN"      # eth2 -> link verso R_NET

# Router NET: connette NET, R_IT e R_ROOT
r_net[0]="NET"         # eth0 -> rete NET
r_net[1]="LINK_IN"     # eth1 -> link da R_IT
r_net[2]="LINK_RN"     # eth2 -> link da R_ROOT
```

---

## Schema delle Reti

| Nome Rete | CIDR            | Contenuto                          |
| --------- | --------------- | ---------------------------------- |
| ROOT      | 192.168.0.0/24  | dnsroot, R_ROOT                    |
| IT        | 192.168.1.0/24  | dnsit, dnsuni, localuni, pc1, R_IT |
| NET       | 192.168.2.0/24  | dnsnet, dnsstart, ..., R_NET       |
| LINK_RI   | 192.168.10.0/24 | R_ROOT ↔ R_IT                      |
| LINK_IN   | 192.168.20.0/24 | R_IT ↔ R_NET                       |
| LINK_RN   | 192.168.30.0/24 | R_ROOT ↔ R_NET                     |

---

## Indirizzi dei Router

```
R_ROOT:
  eth0: 192.168.0.100/24   (rete ROOT)
  eth1: 192.168.10.1/24    (LINK_RI verso R_IT)
  eth2: 192.168.30.1/24    (LINK_RN verso R_NET)

R_IT:
  eth0: 192.168.1.100/24   (rete IT)
  eth1: 192.168.10.2/24    (LINK_RI da R_ROOT)
  eth2: 192.168.20.1/24    (LINK_IN verso R_NET)

R_NET:
  eth0: 192.168.2.100/24   (rete NET)
  eth1: 192.168.20.2/24    (LINK_IN da R_IT)
  eth2: 192.168.30.2/24    (LINK_RN da R_ROOT)
```

---

## Nuovi Indirizzi dei Server DNS

| Server   | Vecchio IP   | Nuovo IP     |
| -------- | ------------ | ------------ |
| dnsroot  | 192.168.0.5  | 192.168.0.5  |
| dnsit    | 192.168.0.1  | 192.168.1.1  |
| dnsuni   | 192.168.0.11 | 192.168.1.11 |
| dnsnet   | 192.168.0.2  | 192.168.2.2  |
| dnsstart | 192.168.0.22 | 192.168.2.22 |

**Attenzione**: dovrete aggiornare anche i file di zona DNS!

---

## File .startup dei Router

```bash
# r_root.startup
ip a add 192.168.0.100/24 dev eth0
ip a add 192.168.10.1/24 dev eth1
ip a add 192.168.30.1/24 dev eth2
ip link set eth0 up
ip link set eth1 up
ip link set eth2 up

# Route verso IT (via LINK_RI) e NET (via LINK_RN)
ip route add 192.168.1.0/24 via 192.168.10.2   # rete IT via R_IT
ip route add 192.168.2.0/24 via 192.168.30.2   # rete NET via R_NET
ip route add 192.168.20.0/24 via 192.168.10.2  # LINK_IN via R_IT
```

---

## File .startup dei Router

```bash
# r_it.startup
ip a add 192.168.1.100/24 dev eth0
ip a add 192.168.10.2/24 dev eth1
ip a add 192.168.20.1/24 dev eth2
ip link set eth0 up
ip link set eth1 up
ip link set eth2 up

# Route verso ROOT (via LINK_RI) e NET (via LINK_IN)
ip route add 192.168.0.0/24 via 192.168.10.1   # rete ROOT via R_ROOT
ip route add 192.168.2.0/24 via 192.168.20.2   # rete NET via R_NET
ip route add 192.168.30.0/24 via 192.168.10.1  # LINK_RN via R_ROOT
```

---

## File .startup dei Router

```bash
# r_net.startup
ip a add 192.168.2.100/24 dev eth0
ip a add 192.168.20.2/24 dev eth1
ip a add 192.168.30.2/24 dev eth2
ip link set eth0 up
ip link set eth1 up
ip link set eth2 up

# Route verso ROOT (via LINK_RN) e IT (via LINK_IN)
ip route add 192.168.0.0/24 via 192.168.30.1   # rete ROOT via R_ROOT
ip route add 192.168.1.0/24 via 192.168.20.1   # rete IT via R_IT
ip route add 192.168.10.0/24 via 192.168.20.1  # LINK_RI via R_IT
```

---

## Modifiche ai .startup dei Server

Ogni server deve:

1. Cambiare il proprio IP
2. Aggiungere il default gateway

```bash
# Esempio: dnsroot.startup
ip address add 192.168.0.5/24 dev eth0
ip link set eth0 up
route add default gw 192.168.0.100 dev eth0
systemctl start named
```

---

## Modifiche ai .startup dei Client

```bash
# pc1.startup (rete IT)
ip address add 192.168.1.111/24 dev eth0
ip link set eth0 up
route add default gw 192.168.1.100 dev eth0

# pc2.startup (rete NET)
ip address add 192.168.2.222/24 dev eth0
ip link set eth0 up
route add default gw 192.168.2.100 dev eth0
```

---

## Aggiornare i File di Zona DNS

I file in `dnsroot/etc/bind/db.root` devono riflettere i nuovi IP:

```
# Prima
dnsit.it.       IN    A    192.168.0.1
dnsnet.net.     IN    A    192.168.0.2

# Dopo
dnsit.it.       IN    A    192.168.1.1
dnsnet.net.     IN    A    192.168.2.2
```

Lo stesso per tutti gli altri file di zona!


---

## Far partire Kathara

```bash
# nella cartella /tmp/reti-lab-kathara/lab5-dns-http-routed
./start-lab.sh
kathara connect pc1
```

```bash
traceroute 192.168.2.112
dig A api.startup.net
curl http://api.startup.net/visitors
```

Da quali router passano i pacchetti? Quale rete attraversa la query DNS?

---

## Wireshark con più reti

Con i router, Wireshark viene connesso a **tutte le reti**:

| Interfaccia | Rete    | Cosa vedi                      |
| ----------- | ------- | ------------------------------ |
| eth1        | ROOT    | Traffico verso dnsroot         |
| eth2        | IT      | Traffico di pc1, dnsit, dnsuni |
| eth3        | NET     | Traffico di pc2, api, frontend |
| eth4        | LINK_RI | Pacchetti tra R_ROOT e R_IT    |
| eth5        | LINK_IN | Pacchetti tra R_IT e R_NET     |
| eth6        | LINK_RN | Pacchetti tra R_ROOT e R_NET   |

Scegli l'interfaccia giusta per vedere il traffico che ti interessa!
