import os

from datetime import datetime
from collectors.node.node_constants import GPU_NUM

def read_data(file_name, collect_time):
    read_cmd = "tail  -n {} {}".format(collect_time, file_name)
    content = os.popen(read_cmd).read().strip()
    rows = content.splitlines()
    result_list = list()
    
    for row in rows:
        result_list.append(row.split(":"))
    return result_list



def npu_common_cal(collect_time, npu_id):
    npu_common_info = read_data(f"data/npu_common_{npu_id}", collect_time)
    
    
    result = list()
    temp_result = []
    
    for i in range(len(npu_common_info)):
        if "timestamp" in npu_common_info[i][0]:
            if len(temp_result) != 0:
                result.append(temp_result)
            temp_result = [int(npu_common_info[i][1].strip()), 0, 0, 0, 0, 0, 0]
        elif "Power" in npu_common_info[i][0]:
            temp_result[1] = float(npu_common_info[i][1].strip())
        elif "Temperature" in npu_common_info[i][0]:
            temp_result[2] = int(npu_common_info[i][1].strip())
        elif "Aicore Usage Rate" in npu_common_info[i][0]:
            temp_result[3] = int(npu_common_info[i][1].strip())  
        elif "Aicore curFreq" in npu_common_info[i][0]:
            temp_result[4] = int(npu_common_info[i][1].strip())
        elif "Memory Usage Rate" in npu_common_info[i][0]:
            temp_result[5] = int(npu_common_info[i][1].strip())  
        elif "HBM Usage Rate" in npu_common_info[i][0]:
            temp_result[6] = int(npu_common_info[i][1].strip()) 
        
    return result
        
    