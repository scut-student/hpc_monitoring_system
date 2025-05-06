## Overview

In order to provide more granular control, the `slurm/` implements a middleware for listening to user submissions, analyzing and processing them, and then handing them over to Slurm for job management and distribution. Specifically, we replaced the submit command `sbatch` in the slurm job script, and all jobs submitted using this command will be sent to the Slurm listener we wrote instead of Slurm itself. The Slurm listener will parse the script for information such as the type of the job, resource configuration, etc., and optimize the configuration for some unreasonable configurations, such as number of nodes requested, number of threads, and amount of memory etc. The new job script is then submitted to Slurm.

This component serves the workload characterization and optimization part of the project and has little impact on system monitoring, so it is not described in detail here.
