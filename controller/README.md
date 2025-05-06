## Overview

The `controller` module implements a non-intrusive control mechanismfor synchronizing multiple monitoring tools. Its primary objective is to align the sampling time points of different tools, ensuring that the recorded server states across tools remain consistent. The workflow is as follows:

1. Launch all specified monitoring tools (e.g., Procfs, IBMC, Perf), each configured to periodically output data to raw data files at a given interval (e.g., 1 second).
2. Once all tools have successfully started and are generating data, set a time barrier (e.g., 10 seconds later) for synchronization.
3. Use Linux's **`inotify`** mechanism to monitor the latest data generation timestamps (in milliseconds) of each raw data file, and calculate the suspension duration required to align all tools at the time barrier.
4. Send a `SIGSTOP` signal to each monitoring tool to pause execution, then send a `SIGCONT` signal after the computed delay to resume synchronized sampling.
5. Repeat steps 3 and 4 for each synchronization cycle (e.g., every 2 seconds) until monitoring ends.

---

## Practical Experience

### Synchronization Interval vs. Sampling Interval

In practice, we observed that the synchronization interval should be slightly larger than the sampling interval used by each monitoring tool. For example, if a collector generates one data sample every second, it is advisable to perform synchronization every 2 seconds. This ensures sufficient time to:

* Observe the latest file change through `inotify`
* Compute the necessary delay for each tool
* Issue `SIGSTOP`/`SIGCONT` signals without interfering with the next sampling window

This slight buffer helps avoid overlapping control signals with the next round of data sampling and ensures smooth operation.

### Behavior of Tools During Suspension

Different monitoring tools exhibit different behaviors when suspended:

* Passive tools (e.g., those triggered by scheduled timers or periodic threads) might **pause sampling completely** when suspended, resuming later from the next full interval
* Active profilers or tools bound to kernel hooks might retain partial sampling states even during suspension, potentially leading to  partial or stale data

As a result, even though data output timestamps can be aligned, the actual profiling windows might still differ slightly. However:

- In short-interval monitoring, even if a deviation occurs, the value is very small. As a result, the data reflect  essentially the same server state
- For longer intervals (e.g., 30 seconds), the tools tend to converge naturally after several synchronizations. Despite minor differences in profiling periods, most data entries are timestamp-aligned, and the average result remains effective

The difference of profiling windows has negligible impact. Certainly, fragmenting the hang operation would be a better way to implement this.

### Synchronization Frequency Tuning

While the initial design aims for  per-sample synchronization, we found that this is  not always necessary. Repeated synchronizations introduce signal handling overhead and could interfere with tools that are not robust to frequent stopping. More importantly, after a few synchronization cycles, most tools are already closely aligned in timing. Hence, further synchronization can be  spaced out. A practical approach is to perform  adaptive or periodic synchronization , e.g.:

* Every 5–10 sampling intervals
* Or based on detecting a time drift threshold (e.g., >200ms difference between tools)

This strategy offers a  balance between precision and system stability, reducing control complexity while maintaining temporal alignment.

### Overhead of Inotify

The use of `inotify` for monitoring file changes introduces  negligible overhead:

* It is an event-driven mechanism implemented in the Linux kernel, not based on active polling
* Its memory and CPU usage remains minimal, even when monitoring dozens or hundreds of files
* `inotify` does not interfere with the data-writing process, ensuring safe and concurrent monitoring

This makes it a reliable and lightweight choice for high-frequency synchronization workflows in real-world monitoring environments.
