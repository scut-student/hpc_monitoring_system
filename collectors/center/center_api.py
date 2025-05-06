import os

import time
from collectors.center.center_constants import *
from collectors.center.center_comm import CenterServer
from collectors.center.center_collector import CenterCollector


    
    
class CenterWorker:
    def __init__(self) -> None:
        self.start_node_collection_time = None
        self.restart_interval = RESTART_TIME
        self.m_center_collector = CenterCollector()
        self.m_center_server = CenterServer()  
        
    def run_cmd_on_nodes(self, cmd, target_node=None):
        self.m_center_server.run_node_cmd(cmd, target_node)      
    
    def connect_nodes(self):
        rtn = self.m_center_server.connect_nodes()
        if rtn == False:
            self.m_center_server.close_nodes()
            exit()
    
    def start_node_collectors(self):
        self.start_node_collection_time = int(time.time())
        self.m_center_server.start_nodes()
    
    def start_center_collectors(self):
        self.m_center_collector.start_collection()
    
    def end_node_collectors(self):
        self.start_node_collection_time = None
        self.m_center_server.stop_nodes()
    
    def end_center_collectors(self):
        self.m_center_collector.end_collection()
        
    def set_kernel_param(self, kernel_dict):
        self.m_center_server.set_kernel_param_cmd(kernel_dict)
    
    def start_kernel_optimization(self):
        self.m_center_server.start_kernel_optimization_cmd()
        
    def end_kernel_optimization(self):
        self.m_center_server.end_kernel_optimization_cmd()
    
    def stop_center(self):
        self.end_node_collectors()
        self.end_center_collectors()
        self.end_kernel_optimization()
    
    def check_restart_node_collectors(self):
        if self.start_node_collection_time is None:
            return

        current_timestamp = int(time.time())
        collector_runtime = current_timestamp - self.start_node_collection_time
        
        if collector_runtime > self.restart_interval:
            self.end_node_collectors()
            time.sleep(5)
            self.connect_nodes()
            self.start_node_collectors()
            time.sleep(COLLECTOR_WARMUP_TIME)
    
    def pull_node_data(self, data_len=MAX_COLLECTED_TIME):
        self.m_center_server.m_nodes_serial_data = {}
        self.m_center_server.pull_data_from_nodes(data_len)
    
    def pull_node_param(self):
        self.m_center_server.pull_param_from_nodes()
    
    def generate_center_data(self, start_time, end_time=None, data_len=MAX_COLLECTED_TIME):
        self.m_center_collector.integrate_collector_data(start_time, end_time, data_len)
    
    def get_collected_job(self):
        return self.m_center_collector.taskid_list
    
    def get_center_data(self):
        return self.m_center_collector.data
    
    def get_node_data(self):
        return self.m_center_server.m_nodes_serial_data
    
    def get_node_param(self):
        return self.m_center_server.m_nodes_param
    
    def save_center_data(self, dir_path=None):
        self.m_center_collector.save_data(save_dir=dir_path)
    
    def save_node_data(self, dir_path=None):
        data = self.get_node_data()
        if dir_path is None:
            LOGGER.write(LOGGER.global_log, "[CenterWorker]: fails to save node data. \
                Please give dir path.")
            return
        for node_id in data:
            if not os.path.exists(dir_path):
                os.system(f"mkdir -p {dir_path}")
            if dir_path.startswith('/'):
                target_dir = dir_path
            else:
                target_dir = os.path.abspath('.') + '/' + dir_path
            if not target_dir.endswith('/'):
                target_dir += '/'
            target_file_name = target_dir+f"{node_id}.csv"
            data[node_id].to_csv(target_file_name, index=False) 
            
    
    
    
        
        
        
    
    
        
        
        
