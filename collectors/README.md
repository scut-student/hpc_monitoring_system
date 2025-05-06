## Overview

`collectors/` is a module for controlling multiple independent monitoring tools, including monitoring start, end and data transfer behaviors. This module is independent of data processing modules such as data aggregation and anomaly detection, and only provides multiple collector workflows and saves the acquired data as data files. Other modules will directly control and process the collector programs and raw files. 

The module architecture is as follows:

```
├── center # the monitoring logic of the control node
│   ├── center_api.py # the API provided for user to implement center monitoring logic
│   ├── center_collector.py # the general definition of center collectors
│   ├── center_comm.py # the behaviors for comminicating with compute nodes
│   ├── center_constants.py # the global variables of center collectors 
│   └── tools # the collectors that should be executed in the control node
├── common # the comminication definition between the control node and compute nodes
│   ├── communicate_constants.py # comminication single types
│   └── connection.py # communication function
└── node # the monitoring logic of the compute node
    ├── node_api.py # the API provided for user to implement node monitoring logic 
    ├── node_collector.py # the general definition of node collectors
    ├── node_comm.py # the behaviors for comminicating with the control node
    ├── node_constants.py # the global variables of node collectors
    └── tools # the collectors that should be executed in the compute node
```



## Tool Architecture

The collector, whether it is a control node or a compute node, contains the following structure:

- `data/`: directory used for temporary storage of data, including
  - `pid/`: the process id of collector program
  - `raw_data/`: the raw data dumped by the program, such as binary files
  - `parse_data/`: the parsed data based on the raw data, such as CSV files
- `<name>_collector.py`: the main minitoring control logic of target tool

Depending on the tool, other specific files may be included, such as data parsing files, monitoring startup scripts, etc.
