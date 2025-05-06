from constants import *
import os
import configparser
import json


conf = configparser.ConfigParser()
conf.read(f"{WORK_DIR}/conf/global.conf", encoding="UTF-8")
DEFAULT_CONCAT_METHOD = conf.get("collectors", "default_concat_method")
SUBCOLLECTOR_DEFAULT_CONCAT_METHOD = conf.get("collectors", "subcollector_default_concat_method")
MAX_COLLECTED_TIME = int(conf.get("collectors", "max_collected_time"))
BLKTRACE_INTERVAL = int(conf.get("collectors", "blktrace_interval"))
MSPROF_INTERVAL = int(conf.get("collectors", "msprof_interval"))


HOSTNAME = os.popen("hostname").read().strip()
if conf.get("collectors", "main_network") == "auto":
    MAIN_NET_INTERFACE = os.popen("ip route | grep default | awk '{print $5}' | head -n 1").read().strip() 
else:
    MAIN_NET_INTERFACE = conf.get("collectors", "main_network")
if conf.get("collectors", "main_disk") == "auto":
    MAIN_DISK = os.popen("cat /proc/diskstats | grep -e 'sd\\|vd\\|hd' | sort -nrk 14 | head -n 1 | awk '{{print $3}}'").read().strip()
else:
    MAIN_DISK = conf.get("collectors", "main_disk")

NODE_ID = os.popen(f"ip addr | grep {MAIN_NET_INTERFACE} | grep inet | awk '{{print $2}}'").read().strip().replace("/24", "")
CORE_NUM = int(os.popen("cat /proc/cpuinfo  | grep processor | wc -l").read())
MEM_CAPACITY = int(float(os.popen(f"cat /proc/meminfo | grep MemTotal | awk '{{print $2/1024/1024}}'").read().strip()))

NUMA_ZONE_NUM = int(os.popen("numactl --hardware | grep cpus | wc -l").read().strip()) # NUMA zone数量

COMM_PORT = conf.get('connections', 'port')

with open(f"{WORK_DIR}/conf/pmu_events.json", 'r') as json_file:
    json_str = json_file.read()
PMU_EVENTS = json.loads(json_str)

with open(f"{WORK_DIR}/conf/ibmc.json", 'r') as json_file:
    json_str = json_file.read()
IBMC_INFO = json.loads(json_str)


if int(os.popen("which nvidia-smi 2> /dev/null  | wc -l").read().strip()) == 0:
    GPU_NUM = 0
else:
    GPU_NUM = int(os.popen("nvidia-smi -L | wc -l").read().strip())
    
if int(os.popen("which npu-smi 2> /dev/null  | wc -l").read().strip()) == 0:
    NPU_NUM = 0
else:
    NPU_NUM = int(os.popen("npu-smi info -l | grep 'NPU ID' | wc -l").read().strip())    

