# Reti – Kathara labs

Kathara labs for the lab lessons of the course Reti (Computer Networks), University of Trento.

## Setup on the lab PCs

Docker and Kathara are already installed. Work in `/tmp`:

```bash
cd /tmp
git clone https://github.com/Marrocco-Simone/reti-lab-kathara
cd reti-lab-kathara
```

`/tmp` is deleted when the PC shuts down. Copy the files that you change to another folder.

On your own PC, install [Docker](https://www.docker.com/) and [Kathara](https://www.kathara.org/).

## Labs

| Folder                 | Lesson | Content                                                                             |
| ---------------------- | ------ | ----------------------------------------------------------------------------------- |
| `lab3-two-pcs`         | 3      | Two PCs in one collision domain, `ping`                                             |
| `lab3-router`          | 3      | Two subnets connected by one router, default gateway                                |
| `lab4-dns-http`        | 4      | DNS hierarchy, HTTP services and Wireshark, all in one subnet                       |
| `lab5-dns-http-routed` | 5      | The same services, with the DNS domains in three subnets connected by three routers |

The slides are in `lab4-dns-http/slides.pdf` and `lab5-dns-http-routed/slides.pdf`.

## Commands

```bash
kathara lstart --noterminals   # start the lab in the current folder
kathara connect pc1            # open a terminal on pc1
kathara lclean                 # stop the lab
```

The `lab4-dns-http` and `lab5-dns-http-routed` labs use custom Docker images. Build them once with `./build-images.sh`, then start the lab with `./start-lab.sh`. Wireshark is on `http://localhost:3000`.
