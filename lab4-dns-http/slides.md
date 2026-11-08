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

title: DNS with HTTP
---

# DNS and HTTP

---

## Setup

Sui PC del laboratorio lavoriamo nella cartella `/tmp`

```bash
cd /tmp
git clone https://github.com/Marrocco-Simone/reti-lab-kathara
cd reti-lab-kathara/lab4-dns-http
./build-images.sh
```

`build-images.sh` crea le immagini Docker di `api`, `frontend` e `llm` (qualche minuto)

**Attenzione**: `/tmp` viene cancellata allo spegnimento del PC. Copiate altrove i file che modificate!

---

## Esploriamo la cartella

```bash
cd /tmp/reti-lab-kathara/lab4-dns-http
code .
```

---

## lab.conf

All'interno di lab conf vediamo tanti servizi diversi

```conf
pc1[0]="A" # pc1 è nel dominio A
pc1[image]="kathara/base" # usa l'immagine docker di base

frontend[0]="A" # frontend è nel dominio A
frontend[image]="dns-lab/frontend" # usa un'immagine creata da build-images.sh

# wireshark
wireshark[bridged]=true
wireshark[port]="3000:3000"
wireshark[image]="lscr.io/linuxserver/wireshark"
```

---

## file .startup

```conf
ip address add 192.168.0.111/24 dev eth0
```

Indica per ogni pc a che indirizzo si trovano, la submask e la interfaccia, più altri comandi da eseguire all'avvio

```conf
# I server DNS avranno qualcosa del tipo
systemctl start named

# I server HTTP avranno qualcosa del tipo
cd /opt/frontend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 80 &
```

---

## DNS Hierarchy

- **dnsroot** (192.168.0.5) - Root DNS server (.)
- **dnsit** (192.168.0.1) - TLD DNS for .it domain
- **dnsnet** (192.168.0.2) - TLD DNS for .net domain
- **dnsuni** (192.168.0.11) - Authoritative DNS for uniroma3.it
- **dnsstart** (192.168.0.22) - Authoritative DNS for startup.net
- **localuni** (192.168.0.110) - Local DNS server for .it zone
- **localstart** (192.168.0.220) - Local DNS server for .net zone

---

## DNS root

Come configuriamo un server DNS?

- **named.conf** e **named.conf.options** sono i file di configurazione del software BIND, usato per fare un server DNS

```
@               IN      NS      ROOT-SERVER.
ROOT-SERVER.	IN	A	192.168.0.5

it.		    IN 	NS	dnsit.it.
dnsit.it.	    IN 	A	192.168.0.1

net.		    IN	NS	dnsnet.net.
dnsnet.net.	    IN	A	192.168.0.2
```

---

## DNS root

Un record _NS_ (_nameserver_) ci dice dove trovare il DNS server per sapere come direzionare i domini.
Un record _A_ ci dice l'indirizzo del server effettivo dell'url del server DNS

--> Arriva una richiesta per un dominio che finisce in .it (pc1.uniroma3.it)
--> Il DNS server per il dominio si trova in dnsit.it
--> L'IP address di dnsit.it è 192.168.0.1

---

## DNS it

```
@                       IN      NS      dnsit.it.
dnsit.it.               IN      A       192.168.0.1

uniroma3.it.            IN      NS      dnsuni.uniroma3.it.
dnsuni.uniroma3.it.     IN      A       192.168.0.11
```

Agisce molto simile, solo che adesso questo DNS gestisce sottodomini di .it

Andrà a contattare il server DNS per uniroma3.it quando arriva una richiesta specifica (come pc1.uniroma3.it)

---

### Client Machines

- **pc1** (192.168.0.111) - Test client in uniroma3.it domain
- **pc2** (192.168.0.222) - Test client in startup.net domain

### Service Nodes

- **api** (192.168.0.212) - Backend API service (api.startup.net)
- **frontend** (192.168.0.213) - Frontend HTML service (frontend.startup.net)
- **llm** (192.168.0.214) - LLM streaming service (llm.startup.net)

---

## Far partire Kathara

```bash
# nella cartella /tmp/reti-lab-kathara/lab4-dns-http di prima
./start-lab.sh
# connettiamoci al pc1
kathara connect pc1
```

Per accedere a Wireshark, aprite Firefox (o un altro web browser) e andate su `http://localhost:3000`, poi scegliete `eth1`.

I comandi dentro lo script principali sono

```bash
kathara lstart --noterminals
kathara lconfig -n wireshark --add A
```

---

## Testiamo DNS con Wireshark!

```bash
dig A dnsit.it
dig A pc2.startup.net
dig A api.startup.net
```

cosa compare con il filtro DNS in Wireshark?

---

## Testiamo HTTP con Wireshark!

```bash
curl http://api.startup.net/visitors
curl http://frontend.startup.net/
```

cosa compare con il filtro HTTP in Wireshark? Cosa succede all'interno della rete?

---

## Testiamo HTTP con Wireshark!

```bash
curl http://api.startup.net/delay?seconds=10
curl --max-time 3 http://api.startup.net/delay?seconds=10
curl http://api.startup.net/payload?chars=1000000
```

Cosa succede se c'è tanto delay? Se c'è un timeout?

In quanti pacchetti TCP viene divisa una risposta lunga? Quanto grandi sono i pacchetti?

---

## Testiamo HTTP con Wireshark!

```bash
curl -N 'http://llm.startup.net/ask?q=What_is_DNS?'
```

Cosa succede se la risposta viene streammata? In quanti pacchetti TCP viene divisa la risposta? Quanto grandi sono i pacchetti?

---

## Diverse sottoreti

Non è realistico che domini diversi siano nello stesso collision domain. Riusciamo a separarli? Che router usereste?

Ricordiamoci come abbiamo fatto scorsa lezione:

```conf
# lab.conf
r1[0]="A"
r1[1]="B"
pc1[0]="A"
pc2[0]="B"
```

_cartella /tmp/reti-lab-kathara/lab3-router_

---

## Diverse sottoreti

```conf
# pc1.startup
ip a add 192.168.0.1/24 dev eth0
ip link set eth0 up
route add default gw 192.168.0.100 dev eth0

# r1.startup
ip a add 192.168.0.100/24 dev eth0
ip link set eth0 up
ip a add 192.168.1.100/24 dev eth1
ip link set eth1 up
```

Per vedere i router connessi da una macchina come pc1, scrivete

```bash
route -n
```

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

## Compito per casa

Separate i tre domini nella cartella `lab4-dns-http`:

1. Modificate `lab.conf` con le tre reti e i tre router
2. Scrivete i `.startup` dei router con le rotte statiche
3. Cambiate gli indirizzi e aggiungete il default gateway a server e client
4. Aggiornate i file di zona DNS

Testate con `ping`, `traceroute`, `dig` e `curl` da `pc1` verso la rete NET
