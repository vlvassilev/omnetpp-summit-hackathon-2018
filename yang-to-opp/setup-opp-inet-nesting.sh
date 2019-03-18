#!/bin/bash -e


# Assuming ~/omnetpp-summit-hackathon-2018 repo is in the home directory.

# Should NOT be executed as root.


# Download, extract, configure, and build OMNeT++
cd
wget https://ipfs.omnetpp.org/release/5.4.1/omnetpp-5.4.1-src-core.tgz
tar -xzvf omnetpp-5.4.1-src-core.tgz
cd omnetpp-5.4.1
./configure WITH_TKENV=no WITH_QTENV=yes WITH_OSG=no WITH_OSGEARTH=no
export PATH=~/omnetpp-5.4.1/bin:$PATH
make -j $(nproc)


# Download and build INET 4.1.0
cd
git clone --branch v4.1.0 --recursive https://github.com/inet-framework/inet.git
cd inet


export INET_ROOT=`pwd`
export PATH=$INET_ROOT/bin:$PATH
export INET_NED_PATH="$INET_ROOT/src:$INET_ROOT/tutorials:$INET_ROOT/showcases:$INET_ROOT/examples"
export INET_OMNETPP_OPTIONS="-n $INET_NED_PATH --image-path=$INET_ROOT/images"


make makefiles
make -j $(nproc)

# Run an example simulation of INET, with an ordinary ethernet switch, as a test
cd examples/ethernet/lans/
inet duplexswitch.ini -c SwitchedDuplexLAN -u Cmdenv # delete the "-u Cmdenv" part for the graphical interface


# Download and build NeSTiNg
cd
git clone https://gitlab.com/ipvs/nesting.git
cd nesting
make makefiles
make -j $(nproc)

# Run an example simulation of NeSTiNg as a test
cd simulations
./runsim example_strict_priority.ini                # run simulation without graphical interface (release)
# ./runsim-qt example_strict_priority.ini              # simulation with the Qt interface (release)


# Install the lxml Python package for the translator script
cd
pip3 install --user lxml
