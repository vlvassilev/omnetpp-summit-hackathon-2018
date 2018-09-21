#!/bin/bash -e

# This script installs all system-wide dependencies of OMNeT++
# (with Qtenv, but without OSG, osgEarth, the IDE and Tkenv),
# and the yang-to-opp utility.

# Should be executed as root.

apt-get update
apt-get -y install build-essential gcc g++ bison flex perl qt5-default tcl-dev tk-dev libxml2-dev zlib1g-dev qt5-default libqt5opengl5-dev git python python3 python3-pip
