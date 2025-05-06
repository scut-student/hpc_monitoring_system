import os

from datetime import datetime
from collectors.node.node_constants import GPU_NUM

def read_data(file_name, collect_time):
    read_cmd = "tail  -n {} {}".format(collect_time, file_name)
    content = os.popen(read_cmd).read().strip()
    rows = content.splitlines()
    result_list = list()
    
    for row in rows:
        result_list.append(row.split())
    # result_list = np.array(result_list)
    return result_list



def gpu_data_cal(collect_time):
    gpu_data_info = read_data('data/gpu_data', collect_time)
    first = True
    result = list()
    temp_result = []
    
    for i in range(len(gpu_data_info)):
        if gpu_data_info[i][0].startswith("#"):
            continue
        gpu_idx = int(gpu_data_info[i][2])
        if first:
            if gpu_idx == 0:
                first = False
            else:
                continue
            
        date_time = gpu_data_info[i][0]+"-"+gpu_data_info[i][1]
        time_obj = datetime.strptime(date_time, '%Y%m%d-%H:%M:%S')
        timestamp = datetime.timestamp(time_obj)
        
        if gpu_idx == 0:
            if len(temp_result) != 0:
                result.append(temp_result)
            temp_result = [timestamp]
        
        gpu_data_info[i] = [-1 if x == "-" else x for x in gpu_data_info[i][3:]]
        temp_result.extend(gpu_data_info[i])
    return result
        
    