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
    time_info = read_data('data/collected_time', collect_time)
    time_info = [list(map(int, info)) for info in time_info]
    return time_info


def cpu_util_cal(collect_time):
    cpu_info = read_data('data/cpu_util', collect_time+1)
    cpu_info = [list(map(int, info)) for info in cpu_info]
    result = list()
    last_info = list()
    is_new = True
    for info_one in cpu_info:
        if is_new:
            last_info = info_one
            is_new = False
            continue
        temp = [ info_one[i]-last_info[i] for i in range(len(info_one)) ]
        total = sum(temp)
        temp = [ i/total for i in temp ]
        result.append(temp)
        last_info = info_one
    return result

def mem_util_cal(collect_time):
    mem_info = read_data('data/mem_util', collect_time)
    mem_info = [list(map(int, info)) for info in mem_info]
    return mem_info


def io_cal(collect_time):
    io_info = read_data('data/io_stat', collect_time+1)
    io_info = [list(map(int, info)) for info in io_info]
    result = list()
    last_info = list()
    is_new = True
    for info_one in io_info:
        if is_new:
            last_info = info_one
            is_new = False
            continue
        temp = [ info_one[i]-last_info[i] for i in range(len(info_one)) ]
        # rrqm/s wrqm/s r/s w/s rMB/s wMB/s
        result_one = [temp[1], temp[5], temp[0], temp[4], temp[2]/2048, temp[6]/2048]
        # avgrq-sz,avgqu-sz,await
        if temp[0]+temp[4] == 0:
            result_one.append(0) 
            result_one.append(temp[10]/1000) 
            result_one.append(0) 
        else:
            result_one.append((temp[2]+temp[6])/(temp[0]+temp[4]))
            result_one.append(temp[10] / 1000)
            result_one.append((temp[3] + temp[7]) / (temp[0] + temp[4]))
        # r-await
        if temp[0] == 0:
            result_one.append(0)
        else:
            result_one.append(temp[3]/temp[0])
        # w-await
        if temp[4] == 0:
            result_one.append(0)
        else:
            result_one.append(temp[7]/temp[4])
        # util
        result_one.append(temp[9]/1000)
        result.append(result_one)
        last_info = info_one
    return result


def network_cal(collect_time):
    network_info = read_data('data/network_stat', collect_time+1)
    network_info = [list(map(int, info)) for info in network_info]
    last_info = list()
    is_new = True
    result = list()
    for info_one in network_info:
        if is_new:
            last_info = info_one
            is_new = False
            continue
        result_one = [ info_one[i]-last_info[i] for i in range(len(info_one)) ]
        result.append(result_one)
        last_info = info_one
    return result



def numa_cal(collect_time):
    numa_info = read_data('data/numa_stat', (collect_time+1)*6)
    result = list()
    count = 0
    is_new = True
    while count < len(numa_info):
        count = count + 6
        info_one = list()
        for num in range(NUMA_ZONE_NUM):
            info_one.extend([int(info[num+1]) for info in numa_info[count:count+6]])
        
        if is_new:
            last_info = info_one
            is_new = False
            continue    
        result_one = [ info_one[i]-last_info[i] for i in range(len(info_one)) ]
        result.append(list(map(int, result_one)))
        last_info = info_one
    return result

