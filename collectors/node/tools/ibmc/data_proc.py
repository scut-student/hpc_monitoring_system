import os

from collectors.node.node_constants import *



def read_data(file_name, collect_time):
    read_cmd = "tail  -n {} {}".format(collect_time, file_name)
    content = os.popen(read_cmd).read().strip()
    rows = content.splitlines()
    result_list = list()
    
    for row in rows:
        result_list.append(row.split())
    # result_list = np.array(result_list)
    return result_list


def collected_time_cal(collect_time):
    time_info = read_data('data/time', collect_time)
    time_info = [list(map(int, info)) for info in time_info]
    return time_info


def power_cal(collect_time):
    power_info = read_data('data/power', collect_time)
    power_info = [list(map(int, info)) for info in power_info]
    return power_info
    

