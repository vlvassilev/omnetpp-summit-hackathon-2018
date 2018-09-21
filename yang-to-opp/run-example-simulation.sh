#!/bin/bash -e

# Assuming that ~/inet and ~/nesting are built

export PATH=~/omnetpp-5.4.1/bin:$PATH

mkdir example-sim -p
cd example-sim
cp ~/omnetpp-summit-hackathon-2018/topology-with-config.xml .

~/omnetpp-summit-hackathon-2018/sim_net topology-with-config.xml --sim-time-limit=1s

opp_scavetool export -T s -f 'name(*capPk*)' -w -F CSV-S -o out.csv results/*.sca
cat out.csv
