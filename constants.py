import os
import configparser


WORK_DIR = os.path.split(os.path.realpath(__file__))[0]
RESULT_DIR = f"{WORK_DIR}/results"
MODEL_DIR = f"{RESULT_DIR}/model"
FILE_DB_DIR = f"{RESULT_DIR}/data"

conf = configparser.ConfigParser()
conf.read(f"{WORK_DIR}/conf/global.conf", encoding="UTF-8")

DEBUG = bool(int(conf.get('global', 'debug')))
NODE_IPS = conf.get('connections', 'node_ips').split(',')
NODE_NAMES = conf.get('connections', 'node_names').split(',')



# get micro-architecture
cpu_arch_info = os.popen("uname -m").read().strip()
if cpu_arch_info == "x86_64":
    cpu_arch_num = os.popen("cat /proc/cpuinfo | grep -v 'model name' | grep 'family\\|model\\|stepping' | sort | uniq | rev | cut -d ':' -f 1").read().splitlines()
    cpu_arch_num = "".join(cpu_arch_num)
elif cpu_arch_info == "aarch64":
    cpu_arch_num = os.popen("cat /proc/cpuinfo | grep 'CPU part' | uniq | cut -d ':' -f 2").read().strip()
cpu_arch_list = {
    "6 58 5 ": "cascade_lake",
    "6 58 6 ": "cascade_lake",
    "6 58 7 ": "cascade_lake",
    "6 58 4 ": "skylake",
    "6 97 1 ": "broadwell",
    "0xd01": "kunpeng920",
    "0xd08": "kunpeng916"
}
CPU_MICRO_ARCH = cpu_arch_list[cpu_arch_num]

from util.logger import Logger

LOGGER = Logger(
    logging=bool(int(conf.get('global', 'logging'))), 
    silent=bool(int(conf.get('global', 'silent_logging'))),
    max_file_num=int(conf.get('global', 'max_log_file'))
)



