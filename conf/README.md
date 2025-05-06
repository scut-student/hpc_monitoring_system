## Overview

The `conf/` primarily controls the monitoring behavior of the system, including:

- `global.conf`: configuration parameters for major components
- `ibmc.json`: the IBMC address of compute nodes
- `mpi_function_type.json`: MPI functions collected in TAU collector
- `pmu_events.json`: performance counter events collected in Perf collector
- `tau_evens.json`: environment variables in TAU collector

## global.conf

[global]

- debug: if print the DEBUG information
- logging: if record the log information
- silent_logging: if output the log to the terminal
- max_log_file: the maximum number of log file

[analysis]

- aggregation_method: data aggregation method, optional value can be "change_point", "mean"
- power_modeling_method: power modeling method, optional value can be "poly"

[collectors]

- max_collected_time: the maximum time of single collection
- restart_time: the interval of restarting sub-collectors to reduce memory occupation
- warmup_time: the warmup time before the data integration
- default_concat_method: multi-collector data padding method, optional calue can be "outer", "inner", "left", "right"
- subcollector_default_concat_method: multi-set data  padding method in a collector, optional calue can be "outer", "inner", "left", "right"
- main_network: the network interface to be profiling, "auto" means choosing the interface with maximum network traffic
- main_disk: the disk to be profiling, "auto" means choosing the disk with maximum I/O throughput
- blktrace_interval: the collection interval for blktrace collector
- msprof_interval: the collection interval for msprof collector
- tau_profile_path: the temp data file path for TAU collector

[connections]

- port: the port number that used for communication of monitoring programs between control node and compute nodes
- node_ips: the ip of all compute nodes
- node_names: the server name of all compute nodes

[slurm]

- port: the port number that used for listening to slurm job scripts
- max_proxy_connections: the maximum number of connections in the slurm listening program
- wait_time: the interval of the slurm listening program to check the completion of jobs
