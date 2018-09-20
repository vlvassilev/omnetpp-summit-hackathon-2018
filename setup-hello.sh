#!/bin/bash -e

apt-get update
apt-get -y install build-essential git python python3 python3-pip gcc g++ bison flex perl qt5-default tcl-dev tk-dev libxml2-dev zlib1g-dev qt5-default libqt5opengl5-dev

# Assuming ~/omnetpp-summit-hackathon-2018 repo directory and ~/omnetpp-5.4.1-src-core.tgz are in home directory
cd
tar -xzvf omnetpp-5.4.1-src-core.tgz
cd omnetpp-5.4.1
./configure WITH_TKENV=no WITH_QTENV=yes WITH_OSG=no WITH_OSGEARTH=no
export PATH=~/omnetpp-5.4.1/bin:$PATH
make -j $(nproc)

# Download and build INET 3.6.4
cd
git clone --branch v3.6.4 --recursive https://github.com/inet-framework/inet.git
cd inet
make makefiles
make -j $(nproc)

# Run an example simulation of INET, with an ordinary ethernet switch
cd examples/ethernet/lans/
./run duplexswitch.ini -c SwitchedDuplexLAN -u Cmdenv # delete the "-u Cmdenv" part for the graphical interface

# Download and build NeSTiNg
cd
git clone https://gitlab.com/ipvs/nesting.git
cd nesting
make makefiles
make -j $(nproc)
# Run an example simulation of NeSTiNg
cd simulations
./runsim example.ini                # run simulation without graphical interface (release)
# ./runsim-qt example.ini                # simulation with the Qt interface (release)

cd

pip3 install --user lxml

mkdir example-sim -p
cd example-sim

cp ~/omnetpp-summit-hackathon-2018/topology-with-config.xml .

~/omnetpp-summit-hackathon-2018/sim_net topology-with-config.xml --sim-time-limit=1s

opp_scavetool export -T s -f 'name(*capPk*)' -w -F CSV-S -o out.csv results/*.sca
cat out.csv
