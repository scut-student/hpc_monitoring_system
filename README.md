# An Organizational Framework for Multiple Monitoring Tools to Improve the Correctness of High Performance Computing Datasets  

## Abstract
High Performance Computing (HPC) has seen significant advancements and widespread application in recent years. To conduct a comprehensive analysis of HPC systems, modern supercomputing environment requires the deployment of multiple monitoring tools to collect diverse HPC datasets. However, existing monitoring systems lack adequate mechanisms to facilitate the coordination among these tools. When data from various tools are aggregated into a single dataset, issues such as time misalignment, increased anomalous data, and low data representativeness arise, leading to datasets that fail to accurately reflect the actual system status. To mitigate the impact of these data correctness issues in the analysis of HPC systems, this paper evaluates the factors affecting data correctness and proposes an organizational framework for integrating multiple monitoring tools. The framework incorporates the time synchronization, anomaly detection, and change point detection to reduce the adverse effects on data correctness during the HPC dataset generation. Extensive experiments demonstrate that the proposed framework outperforms commonly used methods in terms of missing data rates, anomaly percentages, and stability, offering more reliable data support for HPC system analyses.}

![hpc_system](https://github.com/user-attachments/assets/1caf9a06-793a-43ab-96ef-d06f5fe53225)


## Code Availability
The source code and relevant datasets will be made publicly available upon the acceptance of the paper. 

It should be noted that due to the differences in the hardware and software environments of different clusters, the code needs to be modified to run perfectly. The repository is intended to be used as a reference for the implementation of our framework, not as an out-of-the-box tool.
