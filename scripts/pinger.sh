#! /bin/bash
end=$((SECONDS+60000)) # ping each other host once every second for 10mins
# num_servers=11 # 10 plus uph # should change to just 10 and dont ping uph

while [ $SECONDS -lt $end ]; do
#	for i in `seq 1 ${num_servers}`; do
#		ping -c1 10.0.0.${i} #&> /dev/null;
#	done
	# ping -c$((RANDOM % 25)) -W0.1 10.0.0.$1 #&> /dev/null;
	ping -c$((RANDOM % 25)) -W1 10.0.0.$(($((RANDOM % 25))+1)) #&> /dev/null;
	sleep 0.5;
done
