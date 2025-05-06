import pandas as pd
import time
import os
import re

from collectors.center.tools.collector import Collector
from collectors.center.center_constants import *


class SlurmCollector(Collector):
    def __init__(self) -> None:
        super().__init__(
            name="slurm_collector",
            data_type="aggregate",
            tool_layer="server",
            avail_sets={
                "job_basic": ["jobid", "jobname", "priority", "state"],
                "job_res": ["cpu", "mem", "ntasks", "node"],
                "job_time": ["elapsedraw", "submit", "start", "end", "suspended"],
                "user_config": ["nodes(req)", "mem(req)", "mem_per_cpu(req)", "cpus_per_task(req)", \
                                "ntasks_per_node(req)", "distribution(req)"]
            }
        )
        self.taskid_list = []
    
    def start_collection(self, interval=1):
        cur_dir = os.path.abspath('.')
        os.chdir(os.path.split(os.path.realpath(__file__))[0])
        if not os.path.exists("data/pid"):
            os.system("mkdir -p data/pid")
            os.system("mkdir -p data/raw")
            os.system("mkdir -p data/parse")
        self.end_collection()
        os.chdir(cur_dir)
    
    def end_collection(self):
        cur_dir = os.path.abspath('.')
        os.chdir(os.path.split(os.path.realpath(__file__))[0])
        pid_list = os.listdir('./data/pid')
        for pid_file in pid_list:
            pid = open(f"./data/pid/{pid_file}").read()
            os.system(f'kill {pid}')
            os.remove(f"./data/pid/{pid_file}")
        os.chdir(cur_dir)
    
    def raw_data_proc(self, data_len=MAX_COLLECTED_TIME):
        cur_dir = os.path.abspath('.')
        os.chdir(os.path.split(os.path.realpath(__file__))[0] + "/data")
        os.system("rm -rf ./raw/*")
        os.system("rm -rf ./parse/*")
        self.data = pd.DataFrame()
        for taskID in self.taskid_list:
            self.__get_raw_data(taskID)
            raw_data_df = self.__parse_raw_data(taskID)
            script_data_df = self.__parse_script_file(taskID)
            task_df = pd.concat([raw_data_df, script_data_df], axis=1)
            task_df = task_df[[attr for subset in self.avail_sets.values() for attr in subset]]
            self.data = pd.concat([self.data, task_df])
        self.data.reset_index(inplace=True)
        os.chdir(cur_dir)
    
    # parse the slurm scripts that user submitted
    def __parse_script_file(self, taskID):
        """
        Parse the slurm script and store configurations.

        ---
        Attention : Running path should be : ./data/

        ---
        Script file should be like:
          #!/bin/bash
          #SBATCH . ...
        """
        result = pd.DataFrame(columns=self.avail_sets["user_config"])
        try:
            with open(f"./raw/script.{taskID}", "r+") as f:
                data = f.readlines()
                for lineno in range(3, len(data)):
                    if re.match(r"#SBATCH", data[lineno]):
                        varLine = re.split(r"\s|=", data[lineno])
                        varName = varLine[1].replace("-", " ").strip()
                        varValue = varLine[2]
                        if varName == "N" or varName == "nodes":
                            result.loc[0, "nodes(req)"] = varValue
                        elif varName == "cpus per task":
                            result.loc[0, "cpus_per_task(req)"] = varValue
                        elif varName == "ntasks per node":
                            result.loc[0, "ntasks_per_node(req)"] = varValue
                        elif varName == "mem per cpu":
                            result.loc[0, "mem_per_cpu(req)"] = varValue
                        elif varName == "mem":
                            result.loc[0, "mem(req)"] = varValue
                        elif varName == "m" or varName == "distribution":
                            result.loc[0, "distribution(req)"] = varValue
                        else:
                            pass
                    else:
                        break
                result = result.fillna("-1")
                return result
        # Skip if batch script is not recorded.
        except IOError:
            pass
    
    # parse the raw data from sacct command
    def __parse_raw_data(self, taskID):
        """
        Parse the accounting data.

        Jobstep is associated with a srun or mpirun, a single command won't appear in JobID.
         - JobID without a dot : shows the infomation for the whole job
         - JobID like A.batch : shows the information of the node that the script runs on 
         - JobID like A.B : shows the information of jobstep B in job A
        
        Different data has different source:
         - Get from line 3 (Indicates the whole job) : jobid, jobname, elpased, start, end, submit, priority
         - Get from line 6 (Indicates the target task): ntasks, alloctres
         - Analyzed from all lines: state
        
        ---
        Attention :
        1. Running path should be : ./data/
        2. This function should be called after the whole job is finished, or the infomation of jobstep would be incomplete.
        3. Now we use line 3 to parse start, end and elapsed time of a job, but it's not precise enough due to 2 necessary commands
           are taken before the real application. If we need exact time information of the application, we need to parse line 6.

        ---
        An example of raw data:
        
            JobID        JobName                        ElapsedRaw      Start                End                  Submit               Suspended    State                          Priority       NTasks   AllocTRES                                
            ------------ ------------------------------ --------------- -------------------- -------------------- -------------------- ------------ ------------------------------ -------------- -------- ---------------------------------------- 
            1440         tau_cmap_demo                  56              2024-02-21T20:55:04  2024-02-21T20:56:00  2024-02-21T20:55:04  00:00:00     COMPLETED                      4294901165              billing=9,cpu=9,mem=18G,node=3           
            1440.batch   batch                          56              2024-02-21T20:55:04  2024-02-21T20:56:00  2024-02-21T20:55:04  00:00:00     COMPLETED                                     1        cpu=3,mem=6G,node=1                      
            1440.0       hostname                       0               2024-02-21T20:55:04  2024-02-21T20:55:04  2024-02-21T20:55:04  00:00:00     COMPLETED                                     3        cpu=9,mem=18G,node=3                     
            1440.1       hydra_pmi_proxy                50              2024-02-21T20:55:10  2024-02-21T20:56:00  2024-02-21T20:55:10  00:00:00     COMPLETED                                     3        cpu=9,mem=18G,node=3                    
        """
        attributes = ["jobid", "jobname", "elapsedraw", "start", "end", "submit", "suspended", "priority", \
                      "cpu", "mem", "node", "ntasks", "state"]
        attribute_pos = [0, 13, 44, 60, 81, 102, 123, 136, 167, 183, 192, 232]
        with open(f"./raw/sacct.{taskID}", "r+") as f:
            data = f.readlines()
            attribute_origin = []
            attribute_data = {}
            for line in data:
                attribute_origin.append(
                    [line[attribute_pos[i]:(attribute_pos[i + 1] - 1)] for i in range(len(attribute_pos) - 1)])
            
            try:
                # Get infomation from line 3
                wholeJobInfo = attribute_origin[2]
                attribute_data = {
                    "jobid": [taskID],
                    "jobname": [wholeJobInfo[1].strip()],
                    "elapsedraw": [wholeJobInfo[2].strip()],
                    "start": [wholeJobInfo[3].strip()],
                    "end": [wholeJobInfo[4].strip()],
                    "submit": [wholeJobInfo[5].strip()],
                    "suspended": [wholeJobInfo[6].strip()],
                    "priority": [wholeJobInfo[8].strip()],
                }
                
                jobState = wholeJobInfo[7].strip()
                for lineno in range(2, len(attribute_origin)):
                    # result of the job is defined by the first NON-COMPLETED state
                    jobStepState = attribute_origin[lineno][7]
                    if re.match(r"(FAILED)|(CANCELLED)", jobStepState) and jobState == "COMPLETED":
                        jobState = jobStepState
                        break
                attribute_data["state"] = jobState
                
                # Get information from the last line
                # REMARK: in template, the actual job runs at the end of script.
                realTaskInfo = attribute_origin[-1]
                attribute_data["ntasks"] = [realTaskInfo[9].strip()]
                if len(data) >= 6:
                    tres = realTaskInfo[10].split(",")
                    for res in tres:
                        resNV = res.split("=")
                        attribute_data[resNV[0]] = [resNV[1].strip()]
                else:
                    LOGGER.write(LOGGER.global_log,
                                 "[SlurmCollector]: Job step information is incomplete. Job may be cancelled.")
            
            except IndexError:
                LOGGER.write(LOGGER.global_log, "[SlurmCollector]: Job step information not loaded.")
            
            return pd.DataFrame(attribute_data)
    
    # get raw data by sacct command
    def __get_raw_data(self, taskID):
        """
        Get accounting data and slurm script by sacct or scontrol command. sacct by default
         - Accounting data will be stored to : ./data/raw/sacct.jobid
         - Original script will be stored to : ./data/raw/script.jobid
        ---

        Para:
         - taskID : slurm job id
        ---
        Attention : 
        1. Running path should be : ./data/
        2. Result from sacct may be unreliable, especially NTASKS. Use scontrol if you need exact data.
        """
        
        SACCT_ACCT_COMMAND = f"sacct \
            -o jobid%-12,jobname%-30,elapsedraw%-15,start%-20,end%-20,submit%-20,suspended%-12,state%-30,priority%-15,ntasks%-8,alloctres%-40 \
            -j {taskID} \
            > ./raw/sacct.{taskID}"
        SACCT_SCRIPT_COMMAND = f"sacct --batch-script -j {taskID} > ./raw/script.{taskID}"
        # SCONTROL_ACCT_COMMAND = f"scontrol show job {taskID} > ./raw/scontrol.{taskID}"
        os.system(SACCT_ACCT_COMMAND)
        time.sleep(1)
        os.system(SACCT_SCRIPT_COMMAND)
        time.sleep(1)
