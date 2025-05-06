from configparser import ConfigParser
import os
import pickle
import traceback

from collectors.common.communicate_constants import *
from collectors.center.center_constants import *
import pandas as pd
import threading
import socket

from collectors.common.connection import Connection


class CenterServer:
    def __init__(self) -> None:
        self.m_nodes_info = NODE_INFO
        self.m_node_connections = {} # {name: Connection}
        self.m_send_lk = threading.Lock()
        self.m_data_lk = threading.Lock()
        self.m_nodes_serial_data = {} # {name: df}
        self.m_nodes_param = {} # {name: dict}
        
        self.m_stopped = True
        self.m_thread = None
        
    def connect_nodes(self):
        if not self.m_stopped:
            LOGGER.write(LOGGER.global_log, "[CenterServer]: Error, center has started")
            return
        self.m_stopped = False
        
        for node_info in self.m_nodes_info:
            connection = None
            try:
                connection = Connection()
                connection.m_closed = False
                connection.m_name, connection.m_ip, connection.m_port = node_info['name'], node_info['ip'], node_info['port']
                connection.connect_node()
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: {connection.m_ip} connected.")
                
                self.m_node_connections[node_info['name']] = connection
            except Exception as e:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, fail to start connect to {node_info['name']}, {e}")
                connection.close()
                return False
        return True
    
    def close_nodes(self):
        for node_name in self.m_node_connections:
            LOGGER.write(LOGGER.global_log, f"[CenterServer]: Close {node_name} connection.")
            self.m_node_connections[node_name].close()

                
    def start_nodes(self):
        for connection in self.m_node_connections.values():
            try:
                if connection.m_closed:
                    continue 
                
                self.send_begin_cmd(connection)
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: starting {connection.m_ip} collector")
            except socket.timeout:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, timeout for receiving data from node {connection.m_ip}")
            except Exception as e:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: {traceback.print_exc()}")
                connection.close()
                
    
    def stop_nodes(self):
        '''
        停止发送 get 命令，并且向所有 node 发送关闭命令
        '''
        if self.m_stopped:
            LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, center has stopped.")
            return
        
        self.m_stopped = True
        for connection in self.m_node_connections.values():
            try:
                if connection.m_closed:
                    continue 
                res = self.send_stop_cmd(connection)
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Receive {res}.")
                if res != OK:
                    LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, collector "
                                                    f"{connection.m_ip} stopped failed. error result: {res}.")
                else:
                    LOGGER.write(LOGGER.global_log, f"[CenterServer]: Collector {connection.m_ip} stopped.")
            except Exception as e:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, send stop cmd exception: {e}.")
            try:
                connection.close()
            except Exception as e:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, stop connection {e}.")
        LOGGER.write(LOGGER.global_log, f"[CenterServer]: Send stop command to all nodes.")
        
        
    def pull_data_from_nodes(self, data_len):
        ret_data = None
        for connection in self.m_node_connections.values():
            if connection.m_closed:
                continue
            try:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Send get command to "
                                                f"{connection.m_ip} with datalen: {data_len}.")
                ret_data = self.send_getdata_cmd(connection, data_len)
                
                self._append_collector_data(connection.m_ip, ret_data)
            except socket.timeout:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, timeout for "
                                                f"receiving data  from node {connection.m_ip}")
            except Exception as e:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, {traceback.print_exc()}")
                connection.close()
                
    def pull_param_from_nodes(self):
        ret_data = None
        for connection in self.m_node_connections.values():
            if connection.m_closed:
                continue
            try:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Send getparam command to {connection.m_ip}")
                ret_data = self.send_getparam_cmd(connection)
    
                self._append_node_param(connection.m_ip, ret_data)
            except socket.timeout:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, "
                                                f"timeout for receiving data  from node {connection.m_ip}'")
            except Exception as e:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, {traceback.print_exc()}")
                connection.close()
        
    def _append_collector_data(self, node_name, ret_data):
        df = pickle.loads(ret_data)
        self.m_data_lk.acquire(blocking=True)
        
        if node_name not in self.m_nodes_serial_data.keys():
            self.m_nodes_serial_data[node_name] = df
        self.m_nodes_serial_data[node_name] = \
            pd.concat([self.m_nodes_serial_data[node_name], df]).drop_duplicates(subset='time', keep='first').sort_values(by='time').reset_index(drop=True)
        # if df is not None:
        #     print(f'{df.shape} \n {df.head()} \n {df.tail()}')
        self.m_data_lk.release()
        
    def _append_node_param(self, node_name, ret_data):
        param_dict = pickle.loads(ret_data)
        self.m_data_lk.acquire(blocking=True)
        self.m_nodes_param[node_name] = param_dict
        self.m_data_lk.release()
        

       
    def save_nodes_data(self, filename_prefix):
        cur_wd = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        self.m_data_lk.acquire(blocking=True)
        
        for name, df in self.m_nodes_serial_data.items():
            df.to_csv(f'../../result/{filename_prefix}_{name}.csv')
        
        self.m_data_lk.release()
        os.chdir(cur_wd)
    
    def get_nodes_data(self, data_len):
        nodes2df = {}
        self.m_data_lk.acquire(blocking=True)
        
        for name, df in self.m_nodes_serial_data.items():
            nodes2df[name] = df.iloc[-data_len:,:].copy().reset_index(drop=True)
            
        self.m_data_lk.release()
        return nodes2df
        
    def clear_nodes_data(self):
        self.m_data_lk.acquire(blocking=True)
        
        for df in self.m_nodes_serial_data.values():
            df.drop(df.index, inplace=True)
        
        self.m_data_lk.release()
        
    def run_node_cmd(self, cmd, target_node=None):
        for connection in self.m_node_connections.values():
            if target_node is not None and connection.m_ip != target_node:
                continue
            
            if connection.m_closed:
                continue
            try:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Send runcmd command to "
                                                f"{connection.m_ip} with cmd: {cmd}")
                res = self.send_runcmd_cmd(connection, cmd)
                
            except socket.timeout:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, timeout for "
                                                f"receiving data  from node {connection.m_ip}")
            except Exception as e:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, {traceback.print_exc()}")
                connection.close()
        
    def set_kernel_param_cmd(self, kernel_dict):
        for connection in self.m_node_connections.values():
            if connection.m_closed:
                continue
            try:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Send setkernelparam command to "
                                                f"{connection.m_ip} with param: {kernel_dict}")
                res = self.send_setkernelparam_cmd(connection, kernel_dict)
                
            except socket.timeout:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, timeout for "
                                                f"receiving data  from node {connection.m_ip}")
            except Exception as e:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, {traceback.print_exc()}")
                connection.close()
                
    def start_kernel_optimization_cmd(self):
        for connection in self.m_node_connections.values():
            if connection.m_closed:
                continue
            try:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Send startkerneloptimization command to "
                                                f"{connection.m_ip}")
                res = self.send_startkerneloptimization_cmd(connection)
                
            except socket.timeout:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, timeout for "
                                                f"receiving data  from node {connection.m_ip}")
            except Exception as e:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, {traceback.print_exc()}")
                connection.close()
    
    def end_kernel_optimization_cmd(self):
        for connection in self.m_node_connections.values():
            if connection.m_closed:
                continue
            try:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Send endkerneloptimization command to "
                                                f"{connection.m_ip}")
                res = self.send_endkerneloptimization_cmd(connection)
                
            except socket.timeout:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, timeout for "
                                                f"receiving data  from node {connection.m_ip}")
            except Exception as e:
                LOGGER.write(LOGGER.global_log, f"[CenterServer]: Error, {traceback.print_exc()}")
                connection.close()
    
    def send_begin_cmd(self, connection):
        self.m_send_lk.acquire(blocking=True)
        connection.send_to_fd(START_NODE_COLLECTOR)
        ret = connection.receive_from_fd()
        self.m_send_lk.release()
        return ret
    
    def send_stop_cmd(self, connection):
        self.m_send_lk.acquire(blocking=True)
        connection.send_to_fd(STOP_NODE_COLLECTOR)
        ret = connection.receive_from_fd()
        self.m_send_lk.release()
        return ret
    
    def send_getdata_cmd(self, connection, num):
        self.m_send_lk.acquire(blocking=True)
        connection.send_to_fd(GET_SERIAL_DATA+','+str(num))
        ret = connection.receive_from_fd()
        self.m_send_lk.release()
        return ret
    
    def send_getparam_cmd(self, connection):
        self.m_send_lk.acquire(blocking=True)
        connection.send_to_fd(GET_NODE_PARAM)
        ret = connection.receive_from_fd()
        self.m_send_lk.release()
        return ret
    
    def send_runcmd_cmd(self, connection, cmd):
        self.m_send_lk.acquire(blocking=True)
        connection.send_to_fd(RUN_CMD+','+cmd)
        ret = connection.receive_from_fd()
        self.m_send_lk.release()
        return ret
    
    def send_setkernelparam_cmd(self, connection, kernel_dict):
        self.m_send_lk.acquire(blocking=True)
        connection.send_to_fd(SET_KERNEL_PARAM+','+json.dumps(kernel_dict))
        ret = connection.receive_from_fd()
        self.m_send_lk.release()
        return ret
    
    def send_startkerneloptimization_cmd(self, connection):
        self.m_send_lk.acquire(blocking=True)
        connection.send_to_fd(START_KERNEL_OPTIMIZATION)
        ret = connection.receive_from_fd()
        self.m_send_lk.release()
        return ret
    
    def send_endkerneloptimization_cmd(self, connection):
        self.m_send_lk.acquire(blocking=True)
        connection.send_to_fd(END_KERNEL_OPTIMIZATION)
        ret = connection.receive_from_fd()
        self.m_send_lk.release()
        return ret
    
    