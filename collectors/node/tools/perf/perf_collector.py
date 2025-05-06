import os
from collectors.node.tools.collector import Collector
from collectors.node.node_constants import *
from collectors.node.tools.perf.data_proc import *


class PerfCollector(Collector):
    def __init__(self) -> None:
        super().__init__(
            name = "perf_collector",
            data_type = "serial",
            tool_layer = "cpu",
            avail_sets = PMU_EVENTS[CPU_MICRO_ARCH] if CPU_MICRO_ARCH in PMU_EVENTS else {}
        )
        
        
    def start_collection(self, interval=1):
        cur_dir = os.path.abspath('.')
        os.chdir(os.path.split(os.path.realpath(__file__))[0])
        if not os.path.exists("data/pid"):
            os.system("mkdir -p data/pid")
        self.end_collection()
        for data_set in self.collected_sets:
            self.perf_collection(interval, data_set, self.avail_sets[data_set])
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
        
        
        
    def perf_collection(self, interval, target_set, target_perf_events):
        interval = int(interval)
        collect_cmd = f"nice -n -20 perf stat -o ./data/perf_{target_set} -I {interval*1000} -e " + \
            ",".join(target_perf_events) + f" & echo $! > ./data/pid/perf_{target_set}"
        os.system(collect_cmd)
        

    def raw_data_proc(self, data_len=MAX_COLLECTED_TIME):
        cur_dir = os.path.abspath('.')
        os.chdir(os.path.split(os.path.realpath(__file__))[0])
        for data_set in self.collected_sets:
            perf_data = perf_cal(data_len, data_set, self.avail_sets[data_set])
            self.concat_new_data(perf_data, is_sub=1)
        os.chdir(cur_dir)
        
        
            