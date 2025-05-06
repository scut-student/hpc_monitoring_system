## Overview

The anomaly detection module is mainly used to analyze the outlier anomalies and shift anomalies to prevent the data from erroneous information. It is the initial step in the log data generation cycle, and the processed data will be passed to the data aggregation module for data summarization. The workflow is as follows:

1. Receive data from the data aggregation module
2. Perform anomaly detection algorithm based on power model on all data
3. Eliminate anomalous data and pass the data to the data aggregation module
4. Wait for the next call in the log data generation cycle


## Practical Experience

### Model Update

Over time, the mapping between system profiling data and server power consumption may evolve due to hardware aging, workload changes, or software updates. As a result, the anomaly detection model may require adaptive correction to maintain accuracy. Common update strategies include:

* Retraining with newly collected data: rebuild the model from scratch using a fresh dataset that reflects the current system state.
* Incremental training: update the existing model with a stream of new data, preserving past learning while adapting to new patterns.
* Model transfer (transfer learning): fine-tune a previously trained model on a small set of new labeled data from the target system.

Determining the right time to update the model is crucial for balancing detection accuracy and system stability. The following criteria can be used to assess whether a model update is needed:

1. Performs the change-point detection algorithm on the data in a log generation cycle, dividing the data into subdata
2. Averaging all subdata to minimize the impact of anomalies, and the averaged data is considered to contain no erroneous information
3. Input the averaged data into the existing power model to obtain the power value evaluated by the model and compare it with the collected power to calculate the error
4. Perform steps 1-3 in multiple log generation cycles to obtain multiple sets of model test errors
5. Compare the model test error with the test error during model training, and perform model update after exceeding a certain threshold value
