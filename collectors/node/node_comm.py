from configparser import ConfigParser
import sys
import threading
import socket
import traceback
import numpy as np

import pandas as pd

from collectors.common.connection import Connection
from collectors.node.node_constants import COMM_PORT

from constants import LOGGER

class NodeServer:
    def __init__(self) -> None:
        self.m_center_connection = None
        
        self.m_listen_thread = None
        self.m_listen_stopped = True
        
        self.m_request_handler = None # request_handler(request) -> str
    
    def start(self):
        if not self.m_listen_stopped:
            LOGGER.write(LOGGER.global_log, '[NodeServer] Errors: listen thread has started')
            return
        listen_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_fd.settimeout(30)
        listen_fd.bind(('0.0.0.0', int(COMM_PORT)))
        listen_fd.listen(1)
        LOGGER.write(LOGGER.global_log, '[NodeServer]: Start listen thread')

        while True:
            try:
                self.m_listen_stopped = False
                conn_fd, conn_addr = listen_fd.accept()
                conn_fd.settimeout(10)
                self.m_center_connection = Connection()
                self.m_center_connection.m_closed = False
                self.m_center_connection.m_name = 'center'
                self.m_center_connection.m_fd = conn_fd
            except socket.timeout:
                LOGGER.write(LOGGER.global_log, '[NodeServer]: Waiting for center connection')
                continue
            self.m_listen_thread = threading.Thread(target=self.server_loop)
            self.m_listen_thread.start()
            self.m_listen_thread.join()
                
    def stop(self):
        if self.m_listen_stopped:
            LOGGER.write(LOGGER.global_log, '[NodeServer]: Errors: listen thread has stopped')
            return
        
        self.m_listen_stopped = True   
        LOGGER.write(LOGGER.global_log, '[NodeServer]: listen loop stopped')
 
        
    def server_loop(self):
        while not self.m_listen_stopped:
            try:
                data = self.m_center_connection.receive_from_fd()
                if data == '':
                    LOGGER.write(LOGGER.global_log, '[NodeServer]: receive data is None')
                    break
                response = self.m_request_handler(data, self.m_center_connection)
                if self.m_center_connection.m_closed is True:
                    LOGGER.write(LOGGER.global_log, f'[NodeServer] {sys._getframe().f_lineno}: Close connection by handler')
                    break
                if response is None:
                    response = ''
                self.m_center_connection.send_to_fd(response)
            except Exception as e:
                LOGGER.write(LOGGER.global_log, f'[NodeServer] Error: {traceback.print_exc()}')
                break
            
        LOGGER.write(LOGGER.global_log, f'[NodeServer]: close connection')
        self.m_center_connection.close()
                
    def register_request_handler(self, request_handler):
        self.m_request_handler = request_handler