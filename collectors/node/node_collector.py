import pandas as pd
from collectors.node.node_constants import *

from collectors.node.tools.collector import Collector
from collectors.node.tools.ftrace.ftrace_collector import FtraceCollector
from collectors.node.tools.perf.perf_collector import PerfCollector
from collectors.node.tools.proc_fs.proc_fs_collector import ProcFsCollector
from collectors.node.tools.blktrace.blktrace_collector import BlktraceCollector
from collectors.node.tools.ibmc.ibmc_collector import IBMCCollector
from collectors.node.tools.msprof.msprof_collector import MsprofCollector
from collectors.node.tools.nvidia_smi.nvidia_smi_collector import NVidiaSmiCollector
from collectors.node.tools.npu_smi.npu_smi_collector import NpuSmiCollector



class NodeCollector(Collector):
    def __init__(self) -> None:
        self.data = pd.DataFrame()  
        self.is_collecting = False  
        if NODE_ID not in IBMC_INFO:
            IBMC_INFO[NODE_ID] = {}
        self.sub_collectors = {"ibmc_collector": IBMCCollector(IBMC_INFO[NODE_ID]), \
            "ftrace_collector": FtraceCollector(), "perf_collector": PerfCollector(), \
            "proc_fs_collector": ProcFsCollector(), "blktrace_collector": BlktraceCollector(), \
            "msprof_collector": MsprofCollector(), "nvidia_smi_collector": NVidiaSmiCollector(), \
            "npu_smi_collector": NpuSmiCollector()}

        self.config_collectors(None)
        # self.config_collected_sets(None)

    
    def start_collection(self, interval=1) -> None:
        """start collection

        Args:
            interval (int, optional): collection interval. Defaults to 1.
        """
        if self.is_collecting:
            LOGGER.write(LOGGER.global_log, f"[NodeCollector]: Error. Start collection fails, collector is running.")
            return
        LOGGER.write(LOGGER.global_log, f"[NodeCollector]: target disk: {MAIN_DISK}")
        LOGGER.write(LOGGER.global_log, f"[NodeCollector]: target network: {MAIN_NET_INTERFACE}")

        self.is_collecting = True
        for collector in self.sub_collectors.values():
            if not len(collector.collected_sets) == 0:
                LOGGER.write(LOGGER.global_log, f"[NodeCollector]: Start collector: {collector.name}")
                collector.start_collection(interval)
    
    
    def end_collection(self) -> None:
        """end collection
        """
        if not self.is_collecting:
            LOGGER.write(LOGGER.global_log, f"[NodeCollector]: Error, end collection fails, \
                collector is not running.")
            return
        self.is_collecting = False
        for collector in self.sub_collectors.values():
            if not len(collector.collected_sets) == 0:
                LOGGER.write(LOGGER.global_log, f"[NodeCollector]: End collector: {collector.name}")
                collector.end_collection()
            
    def config_collectors(self, target_set_dict:dict=None) -> None:
        """config dataset to be collected

        Args:
            target_set_dict (dict, optional): target dataset, default is None(collect all dataset)
        """
        if target_set_dict is None:
            for collector in self.sub_collectors.values():
                collector.config_collected_sets(None) 
        else:
            for collector in self.sub_collectors:
                if collector in target_set_dict and target_set_dict[collector]:
                    self.sub_collectors[collector].config_collected_sets(None)
                else:
                    self.sub_collectors[collector].config_collected_sets([])
    
    
    def integrate_collector_data(self, data_len:int=MAX_COLLECTED_TIME) -> None:
        """get data

        Args:
            data_len (int, optional): data length. Defaults to MAX_COLLECTED_TIME.
        """
        self.data = pd.DataFrame()
        for collector in self.sub_collectors.values():
            if not len(collector.collected_sets) == 0:
                collector.data = pd.DataFrame()
                collector.raw_data_proc(data_len)
                self.concat_new_data(collector.data)
        self.data.sort_values(by="time", axis=0, ascending=True, inplace=True)
        
        
    def get_data(self, save_dir:str=None) -> pd.DataFrame:
        """save data

        Args:
            save_path (str, optional): data path

        Returns:
            pd.DataFrame: data
        """
        if save_dir:
            if not os.path.exists(save_dir):
                os.system(f"mkdir -p {save_dir}")
            else:
                if save_dir.startswith('/'):
                    target_dir = save_dir
                else:
                    target_dir = os.path.abspath('.') + '/' + save_dir
                if not target_dir.endswith('/'):
                    target_dir += '/'
                    
                serial_data_file = target_dir+"serial_data.csv"
                
                self.data.to_csv(serial_data_file, index=False) 
        return self.data
            
    def get_param(self) -> dict:
        node_param = {
            "hostname": HOSTNAME,
            "node_id": NODE_ID,
            "arch": CPU_MICRO_ARCH,
            "core_num": CORE_NUM,
            "mem_capacity": MEM_CAPACITY,
            "numa_num": NUMA_ZONE_NUM,
            "target_disk": MAIN_DISK,
            "target_net": MAIN_NET_INTERFACE
        }
        return node_param
    
    
    
    