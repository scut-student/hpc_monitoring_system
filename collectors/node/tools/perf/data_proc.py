import os
import pandas as pd


def perf_cal(collect_time, target_set, target_perf_events):
    perf_time_cmd =f"head -n 1 data/perf_{target_set} | cut -d ' ' -f 4- | xargs -I {{}} date -d \"{{}}\" +%s"
    perf_time = os.popen(perf_time_cmd).read()
    perf_cmd = f"tail -n +4 data/perf_{target_set} | grep -v '^#' | tail -n {{}} |"\
            .format(len(target_perf_events)*collect_time)+ "awk '{if ($2!=\"#\") print $1, $2}'"
    perf = os.popen(perf_cmd).read().splitlines()
    result = list()

    count = 0
    while count < len(perf):
        result_one = list()
        result_one.append(int(float(perf[count].split()[0]))+int(perf_time))
        result_one.extend([ info.split()[1].replace(',', '') for info in perf[count:count+len(target_perf_events)] ])
        count = count + len(target_perf_events)
        result.append(list(map(int, result_one)))
    result = pd.DataFrame(result)
    result.columns = ["time"]+target_perf_events
    return result

