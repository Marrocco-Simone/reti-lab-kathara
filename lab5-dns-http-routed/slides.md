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
cd reti-lab-kathara/lab4-dns-http
```

Al primo `./start-lab.sh` Kathara scarica da `ghcr.io` le immagini Docker di `api`, `frontend` e `llm` (qualche minuto)

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

Regola: ogni record **A** con un IP che è cambiato va aggiornato

`dnsroot` resta a 192.168.0.5: i file `db.root` dei server locali non cambiano

Gli IP nuovi sono quelli dei file `.startup`

---

## File di zona da aggiornare

| File di zona                       | Record da aggiornare                       |
| ---------------------------------- | ------------------------------------------ |
| `dnsroot/etc/bind/db.root`         | `dnsit.it`, `dnsnet.net`                   |
| `dnsit/etc/bind/db.it`             | `dnsit.it`, `dnsuni.uniroma3.it`           |
| `dnsnet/etc/bind/db.net`           | `dnsnet.net`, `dnsstart.startup.net`       |
| `dnsuni/etc/bind/db.it.uniroma3`   | `dnsuni`, `pc1`, `localuni`                |
| `dnsstart/etc/bind/db.net.startup` | `dnsstart`, `pc2`, `localstart`, `api`, `frontend`, `llm` |

---

## Esempio: `dnsstart/etc/bind/db.net.startup`

```
; Prima (tutti nella rete A)
dnsstart.startup.net.   IN   A   192.168.0.22
pc2.startup.net.        IN   A   192.168.0.222
api.startup.net.        IN   A   192.168.0.212

; Dopo (rete NET, 192.168.2.0/24)
dnsstart.startup.net.   IN   A   192.168.2.22
pc2.startup.net.        IN   A   192.168.2.222
api.startup.net.        IN   A   192.168.2.212
```

L'IP di ogni record deve essere uguale a quello nel file `.startup` della macchina

---

## Altri file DNS da cambiare

**`resolv.conf`**: ogni macchina chiede al DNS locale **della sua rete**

```
# pc1/etc/resolv.conf (rete IT)
nameserver 192.168.1.110
# pc2, api, frontend, llm: /etc/resolv.conf (rete NET)
nameserver 192.168.2.220
```

**`named.conf.options`** di `localuni` e `localstart`: rispondono solo alle reti elencate

```
allow-recursion { 192.168.0.0/24; };   # prima: solo la rete A
allow-recursion { 192.168.0.0/16; };   # dopo: tutte le reti 192.168.x.x
```

---

## Wireshark con più reti

Wireshark vede solo le reti a cui è collegato

```conf
# lab.conf
wireshark[bridged]=true      # eth0: collegamento al nostro PC
wireshark[port]="3000:3000"  # http://localhost:3000
wireshark[image]="lscr.io/linuxserver/wireshark:4.6.5"
```

`wireshark` non ha `wireshark[0]=...`: lo colleghiamo alle reti **dopo** `kathara lstart`, ogni `--add` crea l'interfaccia successiva

```bash
kathara lconfig -n wireshark --add ROOT   # diventa eth1
kathara lconfig -n wireshark --add IT     # diventa eth2
```

---

## Modifichiamo `start-lab.sh`

La rete A non esiste più. Sostituiamo

```bash
kathara lconfig -n wireshark --add A
```

con una riga per ogni rete:

```bash
kathara lconfig -n wireshark --add ROOT
kathara lconfig -n wireshark --add IT
kathara lconfig -n wireshark --add NET
kathara lconfig -n wireshark --add LINK_RI
kathara lconfig -n wireshark --add LINK_IN
kathara lconfig -n wireshark --add LINK_RN
```

---

## Wireshark con più reti

Dopo la modifica, `start-lab.sh` collega Wireshark a tutte e 6 le reti:

| Interfaccia | Rete    | Cosa vedi                      |
| ----------- | ------- | ------------------------------ |
| eth1        | ROOT    | Traffico verso dnsroot         |
| eth2        | IT      | Traffico di pc1, dnsit, dnsuni |
| eth3        | NET     | Traffico di pc2, api, frontend |
| eth4        | LINK_RI | Pacchetti tra R_ROOT e R_IT    |
| eth5        | LINK_IN | Pacchetti tra R_IT e R_NET     |
| eth6        | LINK_RN | Pacchetti tra R_ROOT e R_NET   |

Dopo `kathara lclean` i collegamenti si perdono: ripartite sempre con `./start-lab.sh`

---

## Catturare su più interfacce

1. Aprite `http://localhost:3000`
2. Nella lista delle interfacce selezionatene più di una con **Ctrl + click**
3. Avviate la cattura

Lo stesso pacchetto compare **una volta per ogni rete** che attraversa

- Colonna dell'interfaccia: campo `frame.interface_name`, tasto destro → Apply as Column
- Ordinate per tempo: catture di reti diverse possono arrivare in disordine

---

## Far partire Kathara

```bash
# nella cartella /tmp/reti-lab-kathara/lab4-dns-http, dopo le modifiche
kathara lclean
./start-lab.sh
kathara connect pc1
```

```bash
traceroute 192.168.2.212
dig A api.startup.net
curl http://api.startup.net/visitors
```

Da quali router passano i pacchetti? Quale rete attraversa la query DNS?

---

# Link con un costo

---

## Ogni link ha un costo

Un costo può essere il ritardo, la banda o il prezzo del collegamento

```
                 [R_ROOT]
              1 /        \ 2
               /          \
          [R_IT]----------[R_NET]
                     5
```

**Domanda**: qual è il percorso migliore da R_IT a R_NET?

---

## Il collegamento diretto non è il migliore

- R_IT → R_NET diretto: costo **5**
- R_IT → R_ROOT → R_NET: costo 1 + 2 = **3**

Le nostre rotte usano ancora il link diretto:

```bash
kathara connect r_it
route -n
```

Quali righe dobbiamo cambiare?

---

## Cambiamo i file .startup

Se rifacciamo `ip route add` su una rete che ha già una rotta:

```
RTNETLINK answers: File exists
```

Cambiamo il **next hop** nei file `.startup`, poi riavviamo il laboratorio

```bash
# r_it.startup
ip route add 192.168.2.0/24 via 192.168.10.1   # NET via R_ROOT (prima 192.168.20.2)

# r_net.startup
ip route add 192.168.1.0/24 via 192.168.30.1   # IT via R_ROOT (prima 192.168.20.1)
ip route add 192.168.10.0/24 via 192.168.30.1  # LINK_RI via R_ROOT (prima 192.168.20.1)
```

---

## Verifica

```bash
kathara lclean
./start-lab.sh
kathara connect pc1
traceroute -n 192.168.2.212
```

```
 1  192.168.1.100    # R_IT
 2  192.168.10.1     # R_ROOT
 3  192.168.30.2     # R_NET
 4  192.168.2.212    # api
```

In Wireshark, cosa passa adesso su LINK_IN (`eth5`) quando facciamo `dig A api.startup.net`?

---

# Dijkstra

---

## Dijkstra: l'idea

1. Il nodo di partenza ha distanza 0
2. Tutti gli altri nodi hanno distanza ∞
3. Visita il nodo con distanza minima non ancora visitato
4. Aggiorna le distanze dei vicini se trovi un percorso più breve
5. Ripeti finché tutti i nodi sono visitati

Ogni router calcola la tabella **partendo da sé stesso**

---

## Aggiungiamo un router

Nuova rete **HOME** (192.168.3.0/24) con `pc3` e il router `r_home`

```
                 [R_ROOT]
              1 /        \ 2
               /          \
          [R_IT]----------[R_NET]
               \     5    /
              1 \        / 1
                 [R_HOME]
                    |
                  [pc3]
```

---

## Nuove reti

| Rete    | Subnet          | Collegamento    | Costo |
| ------- | --------------- | --------------- | ----- |
| HOME     | 192.168.3.0/24  | pc3, R_HOME      | -     |
| LINK_IH | 192.168.40.0/24 | R_IT ↔ R_HOME    | 1     |
| LINK_HN | 192.168.50.0/24 | R_HOME ↔ R_NET   | 1     |

---

## Indirizzi dei nuovi dispositivi

| Dispositivo | Interfaccia | IP            |
| ----------- | ----------- | ------------- |
| R_IT        | eth3        | 192.168.40.1  |
| R_HOME       | eth0        | 192.168.3.100 |
| R_HOME       | eth1        | 192.168.40.2  |
| R_HOME       | eth2        | 192.168.50.1  |
| R_NET       | eth3        | 192.168.50.2  |
| pc3         | eth0        | 192.168.3.33  |

---

## Calcolo a mano da R_IT

| Passo | Nodo visitato | R_IT | R_ROOT | R_NET | R_HOME |
| ----- | ------------- | ---- | ------ | ----- | ----- |
| Init  | -             | 0    | ∞      | ∞     | ∞     |
| 1     | ?             |      |        |       |       |
| 2     | ?             |      |        |       |       |
| 3     | ?             |      |        |       |       |
| 4     | ?             |      |        |       |       |

Compilate la tabella!

---

## Soluzione da R_IT

| Passo | Nodo visitato | R_IT | R_ROOT | R_NET | R_HOME |
| ----- | ------------- | ---- | ------ | ----- | ----- |
| Init  | -             | **0** | ∞     | ∞     | ∞     |
| 1     | R_IT          | 0    | **1**  | **5** | **1** |
| 2     | R_ROOT        | 0    | 1      | **3** | 1     |
| 3     | R_HOME         | 0    | 1      | **2** | 1     |
| 4     | R_NET         | 0    | 1      | 2     | 1     |

- R_NET migliora due volte: 5 → 3 → 2
- Passo 2: R_ROOT e R_HOME pari, l'ordine non conta

---

## Calcolo a mano da R_ROOT

| Passo | Nodo visitato | R_ROOT | R_IT | R_NET | R_HOME |
| ----- | ------------- | ------ | ---- | ----- | ----- |
| Init  | -             | 0      | ∞    | ∞     | ∞     |
| 1     | ?             |        |      |       |       |
| 2     | ?             |        |      |       |       |
| 3     | ?             |        |      |       |       |
| 4     | ?             |        |      |       |       |

Per R_HOME conviene passare da R_IT o da R_NET?

---

## Soluzione da R_ROOT

| Passo | Nodo visitato | R_ROOT | R_IT  | R_NET | R_HOME |
| ----- | ------------- | ------ | ----- | ----- | ----- |
| Init  | -             | **0**  | ∞     | ∞     | ∞     |
| 1     | R_ROOT        | 0      | **1** | **2** | ∞     |
| 2     | R_IT          | 0      | 1     | 2     | **2** |
| 3     | R_NET         | 0      | 1     | 2     | 2     |
| 4     | R_HOME         | 0      | 1     | 2     | 2     |

- R_NET: diretto, costo 2
- R_HOME: via R_IT, costo 1 + 1 = 2 (via R_NET costa 2 + 1 = 3)

---

## Esercizio: aggiungete R_HOME

1. In `lab.conf` aggiungete `r_home`, `pc3`, `r_it[3]` e `r_net[3]`
2. Scrivete `r_home.startup` e `pc3.startup`
3. Aggiungete le interfacce nuove in `r_it.startup` e `r_net.startup`
4. Calcolate Dijkstra da ogni router e scrivete le rotte verso **tutte** le subnet
5. Bonus: aggiungete `pc3.uniroma3.it` nel file di zona di `dnsuni`

Un nodo nuovo richiede `kathara lclean` e poi `./start-lab.sh`

---

## Wireshark sulle reti nuove

Aggiungete in `start-lab.sh`, dopo le altre righe `lconfig`:

```bash
kathara lconfig -n wireshark --add HOME      # eth7
kathara lconfig -n wireshark --add LINK_IH   # eth8
kathara lconfig -n wireshark --add LINK_HN   # eth9
```

---

## Verifica

```bash
kathara connect pc1
traceroute -n 192.168.2.212    # R_IT, R_HOME, R_NET, api

kathara connect dnsroot
traceroute -n 192.168.3.33     # R_ROOT, R_IT, R_HOME, pc3

kathara connect pc2
dig A pc3.uniroma3.it
```

Alcune subnet di collegamento hanno due percorsi con lo stesso costo: entrambi vanno bene

---

## Discussione

- Cosa succede se il link tra R_IT e R_HOME si rompe?
- Le rotte statiche non cambiano da sole: i pacchetti si perdono
- I router reali usano protocolli come **OSPF**, che calcolano Dijkstra in automatico
- Allo stesso modo, i PC reali ricevono IP, default gateway e DNS in automatico con **DHCP**
