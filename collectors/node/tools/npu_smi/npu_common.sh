#!/bin/bash


interval=1
trap 'quit=1' INT QUIT TERM PIPE HUP	# sends execution to end tracing section


while getopts t:n:i: opt
do
	case "$opt" in
		t) time=$OPTARG;;
        i) interval=$OPTARG;;
		n) npu_id=$OPTARG;;
	esac
done


function record_period(){
    current_time=`date +%s`
	echo -e "timestamp : $current_time" >> ./data/npu_common_$npu_id

	common_data=`npu-smi info -t common -i $npu_id`
	echo -e "$common_data" >> ./data/npu_common_$npu_id
}

function main(){
	echo $$ > ./data/pid/npu_common_$npu_id
	cat /dev/null > ./data/npu_common_$npu_id

	secs=0; quit=0

	while (( !quit && secs<time )); do
		(( secs += interval ))
		run_time=`{ time record_period; } 2>&1 | grep real | cut -d 'm' -f 2 | sed 's/s//'`
		sleep_time=`echo $interval-$run_time | bc`
		sleep $sleep_time
	done
}

main
