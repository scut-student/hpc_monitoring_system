import pandas as pd
import numpy as np
from collectors.center.center_constants import *


# 采集器的父类
class Collector:
    def __init__(self, name:str, tool_layer: str, avail_sets: dict, data_type: str) -> None:
        self.name = name  
        self.tool_layer = tool_layer  
        self.avail_sets = avail_sets  
        self.data = {}  
        self.data_type = data_type  
        self.collected_sets = list(self.avail_sets.keys())  

    def config_collected_sets(self, targer_sets=None):
        if targer_sets is None:
            self.collected_sets = list(self.avail_sets.keys())
        else:
            if type(targer_sets) is not list: 
                LOGGER.write(LOGGER.global_log, f"[{self.name}]: Error, 'target_sets' in \
                    function 'config_collected_sets' should be a list.")
            for data_set in targer_sets:
                if data_set not in self.avail_sets.keys():
                    LOGGER.write(LOGGER.global_log, f"[{self.name}]: Error, {data_set} \
                        is not legal set in {self.name}.")
            self.collected_sets = targer_sets
    

