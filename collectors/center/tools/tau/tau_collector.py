import pandas as pd
import time
import os
import re


from collectors.center.tools.collector import Collector
from collectors.center.center_constants import *



class TAUCollector(Collector):
    def __init__(self) -> None:
        super().__init__(
            name = "tau_collector",
            data_type = "aggregate",
            tool_layer = "server",
            avail_sets = {
                "mpi_func": ["name", "time%", "call", "subrs", "exclusive_msec", \
                    "inclusive_total_msec", "inclusive_usec/call"],
                "user_events": ["name", "sample_num", "mean", "max", "min", "std"]
            }
        )
        self.set_environment_var()
        self.taskid_list = []
        self.rank_ip = {}

    def set_environment_var(self):
        pass
    
    
    def start_collection(self, interval=1):
        cur_dir = os.path.abspath('.')
        os.chdir(os.path.split(os.path.realpath(__file__))[0])
        if not os.path.exists("data/pid"):
            os.system("mkdir -p data/pid")
            os.system("mkdir -p data/raw")
            os.system("mkdir -p data/parse")
        self.end_collection()
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
        self.data = {"mpi_func": {}, "user_events": {}}
        for taskid in self.taskid_list:
            self.rank_ip = {}
            os.system("rm -rf ./data/raw/*")
            os.system("rm -rf ./data/parse/*")
            self.pull_raw_data(taskid)
            for ip in os.listdir("./data/raw"):
                for raw_data in os.listdir(f"./data/raw/{ip}"):
                    rank_num = raw_data.split('.')[1]
                    self.rank_ip[f"rank{rank_num}"] = ip
                    os.system(f"pprof -f ./data/raw/{ip}/{raw_data} > \
                        ./data/parse/rank{rank_num}")
            time.sleep(1)
            self.parse_mpi_func(taskid)
            self.parse_user_events(taskid)
        os.chdir(cur_dir)
                
    def config_task_list(self, task_list):
        self.taskid_list = task_list
        
    def pull_raw_data(self, task_id, ip_list=NODE_IPS):
        os.system(f"./file_transfer.sh -r {TAU_PROFILE_PATH}/log.{task_id} -l \
            ./data/raw -i {','.join(ip_list)}")
    
    
    def parse_mpi_func(self, taskid):
        self.data["mpi_func"][taskid] = {}
        attribute = ["time%", "exclusive_msec", "inclusive_total_msec", "call", "subrs", \
                    "inclusive_usec/call", "name"]
        attribute_num = len(attribute)
        for file_name in os.listdir("./data/parse"):
            split_line_num = []
            if not self.rank_ip[file_name] in self.data["mpi_func"][taskid]:
                self.data["mpi_func"][taskid][self.rank_ip[file_name]] = {}
            with open(f"./data/parse/{file_name}") as fp:
                data = fp.readlines()
                for i in range(len(data)):
                    if re.search("-------", data[i]):
                        split_line_num.append(i)
            if len(split_line_num) == 2:
                split_line_num.append(len(data))
            mpi_func_data = data[split_line_num[1]+1: split_line_num[2]]
            
            mpi_func_data = [re.split(r'\s+', line.strip()) for line in mpi_func_data]
            mpi_func_data = [line[:attribute_num-1] + ["_".join(line[attribute_num-1:])] \
                for line in mpi_func_data]
            mpi_func_result = pd.DataFrame(mpi_func_data, columns=attribute)
            mpi_func_result = mpi_func_result[self.avail_sets["mpi_func"]]
            self.data["mpi_func"][taskid][self.rank_ip[file_name]][file_name] = mpi_func_result
            

    
    def parse_user_events(self, taskid):
        self.data["user_events"][taskid] = {}
        attribute = ["sample_num", "max", "min", "mean", "std", "name"]
        attribute_num = len(attribute)

        for file_name in os.listdir("./data/parse"):
            split_line_num = []
            if not self.rank_ip[file_name] in self.data["user_events"][taskid]:
                self.data["user_events"][taskid][self.rank_ip[file_name]] = {}
            with open(f"./data/parse/{file_name}") as fp:
                data = fp.readlines()
                for i in range(len(data)):
                    if re.search("-------", data[i]):
                        split_line_num.append(i)
            if len(split_line_num) > 5:
                user_event_data = data[split_line_num[4]+1: split_line_num[5]]
            else:
                self.data["user_events"][taskid][self.rank_ip[file_name]][file_name] = pd.DataFrame()
                continue
            
            user_event_data = [re.split(r'\s+', line.strip()) for line in user_event_data]
            user_event_data = [line[:attribute_num-1] + ["_".join(line[attribute_num-1:])] \
                for line in user_event_data]
            user_event_result = pd.DataFrame(user_event_data, columns=attribute)
            user_event_result = user_event_result[self.avail_sets["user_events"]]
            self.data["user_events"][taskid][self.rank_ip[file_name]][file_name] = user_event_result
                
            
            
            