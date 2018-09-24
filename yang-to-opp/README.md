# yang-to-opp

This utility converts `.xml` instance data (conforming to `network-topology@2013-10-21.yang`, `ietf-interfaces-ethernet-like@2017-07-03.yang`, `ietf-network-bridge-flows.yang`, `traffic-generator.yang` (in this repo), and `tntapi-netconf-node.yang`) into an OMNeT++ simulation (in the form of one `.ned` and one `.ini` file), utilising modules from the INET Framework (v3.6.4) and the NeSTiNg project.


## Usage:

On a fresh Debian Stretch system (or container):

### Preparation

 - Install git and clone this repository in your home directory (so the root is `~/omnetpp-summit-hackathon-2018`)
 - Download the [OMNeT++ 5.4.1 core release archive](https://www.omnetpp.org/omnetpp/download/30-omnet-releases/2329-omnetpp-5-4-1-core), and put it in your home directory

### Option 1:
 - Change into the `yang-to-opp` directory, and run the `all-in-one.sh` script. It will:
   - Install all dependencies (first asking for your password using `sudo`)
   - Extract and build OMNeT++ (in `~/omnetpp-5.4.1`)
   - Download and build INET and NeSTiNg (in `~/inet` and `~/nesting`)
   - Convert an example .xml file included in this repo to a .ned file
   - Run the example simulation
   - Print some metrics from the simulation results

### Option 2:

 - Change into the `yang-to-opp` directory
 - Perform the initial one-time setup:
   - Run `install-dependencies.sh` as `root`
   - Run `setup-opp-inet-nesting.sh` - NO need for root
 - Run the example simulation
   - Run `run-example-simulation.sh` - NO need for root

### Subsequent simulations
 - Use the `sim_net` script:
   - `~/omnetpp-summit-hackathon-2018/sim_net my-config.xml --sim-time-limit=1s`
   - Query the results in `./results/` using `opp_scavetool`: `opp_scavetool query -T s -f 'name(*capPk*)' -w *.sca -l`

## Limitations

 - The corresponding termination-point/interface/port names must match.
 - Flow matching is done only on destination ethernet address. Matching on input/output port, VLAN ID, and source ethernet address (and masking) needs to be added to the FilteringDatabase module.
 - Traffic classification and scheduling/queuing (conversion from `ietf-network-bridge@2018-07-15.yang`) is not yet implemented.
 - The type of a node (host or switch) is determined using a heuristic, based on the number of termination points it has (=1 -> host, >1 -> switch).
 - Traffic generators are present on host nodes as ethernet applications, and not in every interface of any node.
