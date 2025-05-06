from time import sleep
import sys
import os
import stat


from constants import WORK_DIR
from collectors.node.node_api import NodeWorker


def check_environment():
    # 1. check slurm/data
    data_path = f"{WORK_DIR}/slurm/data"
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    # 2. check slurm/bash
    bash_path = f"{WORK_DIR}/slurm/bash/mkdir-on-all-nodes.sh"
    bash_stat = os.stat(bash_path)
    root_permission = oct(bash_stat.st_mode & 0o777)[-3]
    if root_permission != 0o7:
        os.chmod(bash_path, stat.S_IRWXU)
    # 3. check data
    data_path = f"{WORK_DIR}/data"
    if not os.path.exists(data_path):
        os.mkdir(data_path)


if __name__ == '__main__':
    check_environment()
    nodeWorker = NodeWorker()
    # configure the collectors
    nodeWorker.m_node_collector.config_collectors(
        {"perf_collector": 1, "ibmc_collector": 1, "proc_fs_collector": 1,
         "ftrace_collector": 0, "blktrace_collector": 0, "msprof_collector": 0}
    )
    nodeWorker.start() 
    


