import pandas as pd
import os

from collectors.node.tools.collector import Collector
from collectors.node.node_constants import *
from collectors.node.tools.npu_smi.data_proc import *



class NpuSmiCollector(Collector):
    def __init__(self) -> None:
        npu_data_type = ["time"]
        self.feature_list = ["power", "temp", "aicore_usage", "aicore_freq", "memory_usage", \
            "hbm_usage"]
        for i in range(NPU_NUM):
            npu_data_type.extend([f"{feature}_{i}" for feature in self.feature_list])
        
        super().__init__(
            name = "npu_smi_collector",
            data_type = "serial",
            tool_layer = "server",
            avail_sets = {"npu_common": npu_data_type}
        )
    
    def start_collection(self, interval=1):
        cur_dir = os.path.abspath('.')
        os.chdir(os.path.split(os.path.realpath(__file__))[0])
        if not os.path.exists("data/pid"):
            os.system("mkdir -p data/pid")
        self.end_collection()
        for data_set in self.collected_sets:
            if data_set == "npu_common":
                for i in range(NPU_NUM):
                    os.system(f"nice -n -20 ./npu_common.sh -t {MAX_COLLECTED_TIME} \
                        -i {interval} -n {i} &")
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
            if data_set == "npu_common":
                for i in range(NPU_NUM):
                    npu_data = npu_common_cal(13*data_len, i)
                    npu_data = pd.DataFrame(npu_data)
                    npu_data.columns = ["time"] + [f"{feature}_{i}" for feature in self.feature_list]
                    self.concat_new_data(npu_data, is_sub=1)
        os.chdir(cur_dir)
                
                

