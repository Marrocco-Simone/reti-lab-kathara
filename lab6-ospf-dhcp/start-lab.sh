#!/usr/bin/env bash
kathara lstart --noterminals

# Connect Wireshark to every network: eth1 = first network in the list below, and so on
kathara lconfig -n wireshark --add ROOT   # eth1
kathara lconfig -n wireshark --add IT   # eth2
kathara lconfig -n wireshark --add NET   # eth3
kathara lconfig -n wireshark --add HOME   # eth4
kathara lconfig -n wireshark --add LINK_ROOT_1   # eth5
kathara lconfig -n wireshark --add LINK_IT_1   # eth6
kathara lconfig -n wireshark --add LINK_IT_2   # eth7
kathara lconfig -n wireshark --add LINK_1_2   # eth8
kathara lconfig -n wireshark --add LINK_1_3   # eth9
kathara lconfig -n wireshark --add LINK_2_4   # eth10
kathara lconfig -n wireshark --add LINK_3_4   # eth11
kathara lconfig -n wireshark --add LINK_3_NET   # eth12
kathara lconfig -n wireshark --add LINK_4_NET   # eth13
kathara lconfig -n wireshark --add LINK_4_HOME   # eth14
kathara lconfig -n wireshark --add LINK_2_HOME   # eth15

echo "Wireshark: http://localhost:3000"
