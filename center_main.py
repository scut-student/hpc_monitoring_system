from time import sleep
import datetime
import argparse
import signal

from collectors.center.center_api import CenterWorker


def end_collection(signum, frame):
    # center.stop_center()
    exit(0)


if __name__ == '__main__':
    # parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=60)
    parser.add_argument("--time", type=int, default=600)
    args = parser.parse_args()
    collection_interval = args.interval
    collection_time = args.time
    
    # regist signal
    signal.signal(signal.SIGINT, end_collection)   
    signal.signal(signal.SIGTERM, end_collection) 

    # start collection
    center = CenterWorker()
    center.m_center_collector.config_collectors({"ibmc_collector": 0, "tau_collector": 1, \
        "slurm_collector": 1})
    
    center.connect_nodes()
    center.pull_node_param()
    center.start_node_collectors()
    center.start_center_collectors()
    count = 0
    
    while count <= collection_time:
        sleep(collection_interval)
    
        center.pull_node_data(collection_interval)
        current_time = datetime.datetime.now().strftime("%Y-%M-%DT%H:%M:%S")
        center.generate_center_data(start_time=current_time)
        
        node_data = center.get_node_data()
        node_param = center.get_node_param()
        center_data = center.get_center_data()
            
        print(node_param)
        print(node_data)
        print(center_data)
        
        count += collection_interval
    
    
    

