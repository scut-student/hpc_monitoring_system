import pandas as pd
from datetime import datetime
import re

from collectors.center.center_constants import *

from collectors.center.tools.collector import Collector

from collectors.center.tools.tau.tau_collector import TAUCollector
from collectors.center.tools.ibmc.ibmc_collector import IBMCCollector
from collectors.center.tools.slurm.slurm_collector import SlurmCollector


class CenterCollector(Collector):
    def __init__(self) -> None:
        self.data = {}  
        self.is_collecting = False  
        self.taskid_list = []
        self.sub_collectors = {"ibmc_collector": IBMCCollector(IBMC_INFO), "tau_collector": TAUCollector(),\
            "slurm_collector": SlurmCollector()}

        self.config_collectors(None)
        # self.config_collected_sets(None)

    
    def start_collection(self, interval=1) -> None:
        """start collection

        Args:
            interval (int, optional): collection interval. Defaults to 1.
        """
        if self.is_collecting:
            LOGGER.write(LOGGER.global_log, f"[CenterCollector]: Error, start collection fails, \
                collector is running.")
            return
        self.is_collecting = True
        for collector in self.sub_collectors.values():
            if not len(collector.collected_sets) == 0:
                LOGGER.write(LOGGER.global_log, f"[CenterCollector]: Start {collector.name} collector.")
                collector.start_collection(interval)
    
    
    def end_collection(self) -> None:
        """end collection
        """
        if not self.is_collecting:
            LOGGER.write(LOGGER.global_log, f"[CenterCollector]: Error, end collection fails, \
                collector is not running.")
            return
        self.is_collecting = False
        for collector in self.sub_collectors.values():
            if not len(collector.collected_sets) == 0:
                LOGGER.write(LOGGER.global_log, f"[CenterCollector]: End {collector.name} collector.")
                collector.end_collection()
                
                
    def config_collectors(self, target_set_dict:dict=None) -> None:
        """config dataset to be collected

        Args:
            target_set_dict (dict, optional): target dataset, default is None(collecting all dataset)
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
    
        
    def integrate_collector_data(self, start_time, end_time=None, data_len:int=MAX_COLLECTED_TIME) -> None:
        """get collected data

        Args:
            data_len (int, optional): data length. Defaults to MAX_COLLECTED_TIME.
        """
        self.data = {}
        self.set_taskid_by_time(start_time, end_time)
        LOGGER.write(LOGGER.global_log, f"[CenterCollector]: Get task ids {self.taskid_list}")

        for collector in self.sub_collectors.values():
            if not len(collector.collected_sets) == 0:
                collector.data = {}
                if collector.name == "tau_collector" or "slurm_collector":
                    collector.taskid_list = self.taskid_list
                collector.raw_data_proc(data_len)
                self.data[collector.name] = collector.data
        
        
    def save_data(self, save_dir:str=None) -> pd.DataFrame:
        """save data to disk

        Args:
            save_path (str, optional): data path

        Returns:
            pd.DataFrame: data
        """
        if save_dir is None:
            LOGGER.write(LOGGER.global_log, "[CenterCollector]: fails to save center data. \
                Please give dir path.")

        else:
            if not os.path.exists(save_dir):
                LOGGER.write(LOGGER.global_log, "[CenterCollector]: Error, dir path in function \"get_data\" not exists.")
            else:
                if save_dir.startswith('/'):
                    target_dir = save_dir
                else:
                    target_dir = os.path.abspath('.') + '/' + save_dir
                if not target_dir.endswith('/'):
                    target_dir += '/'
                
                for collector_type in self.data:
                    if collector_type == "ibmc_collector":
                        self.save_ibmc_data(target_dir)
                    elif collector_type == "tau_collector":
                        self.save_tau_data(target_dir)
                    elif collector_type == "slurm_collector":
                        self.save_slurm_data(target_dir)

                    
    def save_ibmc_data(self, dir_path: str):
        ibmc_data = self.data["ibmc_collector"]
        os.system(f"mkdir -p {dir_path}/ibmc")
        for ip in ibmc_data:
            ibmc_data[ip].to_csv(f"{dir_path}/ibmc/{ip}.csv", index=False)


    def save_tau_data(self, dir_path: str):
        mpi_func_data = self.data["tau_collector"]["mpi_func"]
        user_events_data = self.data["tau_collector"]["user_events"]
        for task_id in mpi_func_data:
            for ip in mpi_func_data[task_id]:
                for rank in mpi_func_data[task_id][ip]:
                    target_dir = f"{dir_path}/tau/{task_id}/{ip}/{rank}"
                    os.system(f"mkdir -p {target_dir}")
                    mpi_func_data[task_id][ip][rank].to_csv(f"{target_dir}/mpi_func.csv", index=False)
                    user_events_data[task_id][ip][rank].to_csv(f"{target_dir}/user_events.csv", index=False)
        
    
    def save_slurm_data(self, dir_path: str):
        slurm_data = self.data["slurm_collector"]
        os.system(f"mkdir -p {dir_path}/slurm")
        slurm_data.to_csv(f"{dir_path}/slurm/slurm.csv", index=False)
        
        
    def set_taskid_by_time(self, start_time: str, end_time: str):
        """
        Get the jobid of all the jobs that ran in the given period of time.

        Args:
            start_time: a string indicates the beginning of the time period
            end_time: a string indicates the end of the time period. default is _start_time+1D

        Time should be like "YYYY-MM-DDTHH-MM-SS". An example: 2000-01-01T00:00:00
        """
        self.taskid_list = []
        sacct_start = "2023-01-01T00:00:00"
        sacct_end = "2023-01-02T00:00:00"
        try:
            datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
            sacct_start = start_time
            # EndTime is StartTime+1D by default
            if end_time is None:
                sacct_end = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            else:
                datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")
                sacct_end = end_time
        except IndexError:
            pass
        except ValueError:
            pass
        
        self.__parse_sacct_jobid(f"sacct -S {sacct_start} -E {sacct_end} -o jobid%10,state%20")

    def __parse_sacct_jobid(self, command: str):
        """
        Run the sacct command and parse its result, and add jobid to taskid_list. 
        """
        result = os.popen(command).read().split("\n")
        cur_id = ""
        for line in result:
            line_id = line[0:10].strip()
            state = line[11:].strip()
            line_res = re.search(r"\d+", line_id)
            if line_res is None:
                continue
            else:
                line_id = line_res.group()
    
            if line_id != cur_id:
                cur_id = line_id
                if re.match(r"(FAILED)|(CANCELLED)|(COMPLETED)", state):
                    self.taskid_list.append(line_id)
            else:
                pass
            