#!/bin/bash -e


# Assuming ~/omnetpp-summit-hackathon-2018 repo and
# ~/omnetpp-5.4.1-src-core.tgz are in the home directory.

# Should NOT be executed as root.


# Extract, configure, and build OMNeT++
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

# Run an example simulation of INET, with an ordinary ethernet switch, as a test
cd examples/ethernet/lans/
./run duplexswitch.ini -c SwitchedDuplexLAN -u Cmdenv # delete the "-u Cmdenv" part for the graphical interface


# Download and build NeSTiNg
cd
git clone https://gitlab.com/ipvs/nesting.git
cd nesting
make makefiles
make -j $(nproc)

# Run an example simulation of NeSTiNg as a test
cd simulations
./runsim example.ini                # run simulation without graphical interface (release)
# ./runsim-qt example.ini                # simulation with the Qt interface (release)


# Install the lxml Python package for the translator script
cd
pip3 install --user lxml
