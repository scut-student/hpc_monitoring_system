import os
import pickle
import traceback
import numpy as np
import pandas as pd
from collectors.node.node_collector import NodeCollector
from collectors.node.node_comm import NodeServer

from collectors.common.communicate_constants import *
from collectors.node.node_constants import *

class NodeWorker:
    def __init__(self) -> None:
        self.m_node_collector = NodeCollector()
        self.m_node_server = NodeServer()
        self.m_node_server.register_request_handler(self.request_handler)

    def start(self):
        self.m_node_server.start()
    
    def request_handler(self, request, connection) -> str:
        LOGGER.write(LOGGER.global_log, f"[NodeWorker]: receive command: {request}")
        
        if request == START_NODE_COLLECTOR:
            self.m_node_collector.start_collection()
            LOGGER.write(LOGGER.global_log, f"[NodeWorker]: start collector")
            return OK
            
        elif request.startswith(GET_SERIAL_DATA):
            df = self.getdata_handler(int(request.split(',')[-1]))
            if df is None:
                LOGGER.write(LOGGER.global_log, f"[NodeWorker]: Get empty data from collector, \
                    closing connection to Center Node")
                connection.close()
                return None
            else:
                # print(f'send df: {df.shape} \n {df.head()} \n {df.tail()}')
                return pickle.dumps(df, pickle.HIGHEST_PROTOCOL)
            
        elif request == GET_NODE_PARAM:
            param_dict = self.getparam_handler()
            if param_dict is None:
                LOGGER.write(LOGGER.global_log, f"[NodeWorker]: Get empty param from collector, \
                    closing connection to Center Node")
                connection.close()
                return None
            else:
                return pickle.dumps(param_dict, pickle.HIGHEST_PROTOCOL)
            
        elif request == STOP_NODE_COLLECTOR:
            LOGGER.write(LOGGER.global_log, f"[NodeWorker]: Stop collector and server.")
            self.m_node_collector.end_collection()
            self.m_node_server.stop()
            return OK
        
        elif request.startswith(RUN_CMD):
            cmd = str(request.split(',')[-1])
            LOGGER.write(LOGGER.global_log, f"[NodeWorker]: Run cmd: {cmd}.")
            os.system(cmd)
            return OK
            
        elif request.startswith(SET_KERNEL_PARAM):
            kernel_param = json.loads(','.join(request.split(',')[1:]))
            LOGGER.write(LOGGER.global_log, f"[NodeWorker]: Get kernel param: {kernel_param}.")
            for param in kernel_param:
                os.system(f"sysctl -w {param}={kernel_param[param]}")
            return OK
        else:
            LOGGER.write(LOGGER.global_log, f"[NodeWorker]: Error, receive unknown command: {request}")

    def getdata_handler(self, num) -> pd.DataFrame:
        try:
            if num < 0:
                self.m_node_collector.integrate_collector_data()
            else:
                self.m_node_collector.integrate_collector_data(num)
        except:
            LOGGER.write(LOGGER.global_log, f"[NodeWorker]: {traceback.format_exc()}")

            self.m_node_collector.end_collection()
            return None
        df = self.m_node_collector.data
        return df

    def getparam_handler(self) -> dict:
        param_dict = self.m_node_collector.get_param()
        return param_dict
    
        
        