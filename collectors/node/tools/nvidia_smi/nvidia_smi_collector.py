import pandas as pd
import os

from collectors.node.tools.collector import Collector
from collectors.node.node_constants import *
from collectors.node.tools.nvidia_smi.data_proc import *



class NVidiaSmiCollector(Collector):
    def __init__(self) -> None:
        gpu_data_type = ["time"]
        feature_list = ["pwr", "gtemp", "mtemp", "sm", "mem", "enc", "dec", \
                "jpg", "ofa", "mclk", "pclk"]
        for i in range(GPU_NUM):
            gpu_data_type.extend([f"{feature}_{i}" for feature in feature_list])
        
        super().__init__(
            name = "nvidia_smi_collector",
            data_type = "serial",
            tool_layer = "server",
            avail_sets = {"gpu_data": gpu_data_type}
        )
    
    def start_collection(self, interval=1):
        cur_dir = os.path.abspath('.')
        os.chdir(os.path.split(os.path.realpath(__file__))[0])
        if not os.path.exists("data/pid"):
            os.system("mkdir -p data/pid")
        self.end_collection()
        for data_set in self.collected_sets:
            if data_set == "gpu_data":
                os.system(f"nice -n -20 nvidia-smi dmon -d {interval} -c {MAX_COLLECTED_TIME} -o DT \
                    > ./data/gpu_data & echo $! > ./data/pid/gpu_data")
        os.chdir(cur_dir)
        
    
    def end_collection(self):
        cur_dir = os.path.abspath('.')
        os.chdir(os.path.split(os.path.realpath(__file__))[0])
        pid_list = os.listdir('./data/pid')
        for pid_file in pid_list:
            pid = open(f"./data/pid/{pid_file}").read()
            os.system(f'kill {pid}')
            os.remove(f"./data/pid/{pid_file}")
        os.chdir(cur_dir)
        
        
    def raw_data_proc(self, data_len=MAX_COLLECTED_TIME):
        cur_dir = os.path.abspath('.')
        os.chdir(os.path.split(os.path.realpath(__file__))[0])
        for data_set in self.collected_sets:
            if data_set == "gpu_data":
                extra_len = 2 * int(data_len / 20 + 1)
                gpu_data = gpu_data_cal(GPU_NUM*data_len+extra_len)
                gpu_data = pd.DataFrame(gpu_data)
                gpu_data.columns = self.avail_sets["gpu_data"]
                self.concat_new_data(gpu_data, is_sub=1)
        os.chdir(cur_dir)
                
                

