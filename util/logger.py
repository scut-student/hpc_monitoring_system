import os
import datetime

from constants import RESULT_DIR

LOG_DIR = f"{RESULT_DIR}/log"


class Logger():
    def __init__(self, logging, silent, max_file_num) -> None:
        self.logging = logging
        self.silent = silent
        self.max_file_num = max_file_num
        
        self.current_date = 0
        
        self.global_log = LOG_DIR + "/global/global.log"
        self.analysis_log = LOG_DIR + "/analysis/analysis.log"
        self.optimization_log = LOG_DIR + "/optimization/optimization.log"
        self.log_list = ["global", "analysis", "optimization"]
        
        self.delimiter = "============================================================"

        for log_type in self.log_list:
            os.system(f"mkdir -p {LOG_DIR}/{log_type}")
        
        self.file_link()
        
    def reconstruct(self):
        os.system(f"rm -rf {LOG_DIR}/*")
        self.file_link()
                
    
    def file_link(self):
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        if self.current_date == current_date:
            return
        else:
            for log_type in self.log_list:
                link_log_file = f"{LOG_DIR}/{log_type}/{log_type}.log"
                new_log_file = f"{LOG_DIR}/{log_type}/{log_type}_{current_date}.log"
                old_log_file = f"{LOG_DIR}/{log_type}/{log_type}_{self.current_date}.log"
                if not os.path.exists(new_log_file):
                    os.system(f"touch {new_log_file}")
                os.system(f"ln -sf {new_log_file} {link_log_file}")
                
                if os.path.exists(old_log_file):
                    if os.path.getsize(old_log_file) == 0:
                        os.system(f"rm -f {old_log_file}")
                        
            self.current_date = current_date
            self.delete_redundant_log()
                
                
    def delete_redundant_log(self):
        for log_type in self.log_list:
            file_list = sorted(os.listdir(f"{LOG_DIR}/{log_type}"))
            file_list.remove(f"{log_type}.log")
            delete_num = len(file_list) - self.max_file_num
            if delete_num > 0:
                for i in range(delete_num):
                    print(f"remove log {LOG_DIR}/{log_type}/{file_list[i]}")
                    os.system(f"rm -f {LOG_DIR}/{log_type}/{file_list[i]}")

                
    def write(self, log_path, message):
        if not self.silent:
            if log_path == self.global_log:
                print(message)
        
        if self.logging:
            current_time = datetime.datetime.now().strftime("[%H:%M:%S]")
            with open(log_path, 'a') as f:
                f.write(current_time + message + '\n')
        
            
                


    
    


