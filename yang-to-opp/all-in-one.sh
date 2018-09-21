#!/bin/bash -e

sudo ./install-dependencies.sh

./setup-opp-inet-nesting.sh

./run-example-simulation.sh
