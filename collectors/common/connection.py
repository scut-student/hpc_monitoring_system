from collectors.common.communicate_constants import *
import socket

from constants import LOGGER

class Connection:
    def __init__(self) -> None:
        self.m_closed = True 
        
        self.m_name = None
        self.m_ip = None
        self.m_port = None
        self.m_fd = None
        
        self.m_unread_content = ''
    
    def close(self):
        self.m_closed = True
        
        self.m_name = None
        self.m_ip = None
        self.m_port = None
        if self.m_fd is not None:
            LOGGER.write(LOGGER.global_log, f'[Connection]: close fd')
            self.m_fd.close()
        self.m_fd = None
        
    def send_to_fd(self, msg):
        if self.m_fd is None:
            LOGGER.write(LOGGER.global_log, f'[Connection]: Error, fd is none, cannot send msg')
        # msg += 'EOF'
        type = None
        if isinstance(msg, bytes):
            type = 0
            send_bytes = msg
        else:
            type = 1
            send_bytes = msg.encode()
        # print(f'[Connection] Debug: send msg and bytes length: {len(msg), len(send_bytes)}')
        self.m_fd.send(len(send_bytes).to_bytes(32, 'big'))
        self.m_fd.send(type.to_bytes(32, 'big'))
        
        for begin_idx in range(0, len(send_bytes), 4096):
            self.m_fd.send(send_bytes[begin_idx: begin_idx+4096])
        
    def receive_from_fd(self):
        '''
        Receive messages from the other side until a complete message is received or 
        the connection is closed.
        If (1) the other side closes the connection, and 
        (2) the Connection is closed: an exception is thrown, which is handled by the caller.
        '''
        # print(f'[Connection] Debug: begin receive data.')
        ret_data = None
        cnt = 1
        
        while not self.m_closed:
            try:                    
                # print(f'[Connection] Debug: wait for receive.')
                msg_len = int.from_bytes(self.m_fd.recv(32), 'big')
                type = int.from_bytes(self.m_fd.recv(32), 'big')
                block_len = max(4096, int(msg_len / 10))
                recv_bytes = b''
                while len(recv_bytes) < msg_len:
                    ret_byte = self.m_fd.recv(block_len)
                    cnt += 1
                    if ret_byte == b'' or ret_byte is None:
                        raise Exception('node close connection')
                    recv_bytes += ret_byte
                    # print(f'[Connection] Debug: receive bytes len {len(recv_bytes)}.')
                # json_data += ret
                if type == 1:
                    ret_data = recv_bytes.decode()
                else:
                    ret_data = recv_bytes
                break
                # if 'EOF' in ret:
                #     json_datas = json_data.split('EOF')
                #     json_data, self.m_unread_content = json_datas[0], json_datas[1]
                #     break
            except socket.timeout:
                # print('[Connector]: timeout for receiving')   
                pass
        return ret_data
    
    def connect_node(self):
        conn_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_fd.connect((self.m_ip, self.m_port))
        conn_fd.settimeout(5)
        self.m_fd = conn_fd
        return conn_fd
    