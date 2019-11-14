# #!/usr/bin/env bash
# #
# # File: pylb.sh
# #
# # Description   : Start and setup load balancing service
# # Created by    : Quinn Burke (qkb5007@psu.edu)
# # Date          : January 2019
# # Last Modified : December 2019


# ### Globals ###

# python apps/loadbalancer/load_balancer.py --enableStatistics;
# check VipsResource.java for supported json fields
# member port doesnt seem like its used
# curl -X POST -d '{"id":"1","name":"vip1","protocol":"icmp","address":"10.0.0.100","port":"1"}' http://localhost:8080/quantum/v1.0/vips/
# curl -X POST -d '{"id":"1","name":"pool1","protocol":"icmp","vip_id":"1"}' http://localhost:8080/quantum/v1.0/pools/
# curl -X POST -d '{"id":"1","address":"10.0.0.1","port":"1","pool_id":"1"}' http://localhost:8080/quantum/v1.0/members/
# curl -X POST -d '{"id":"2","address":"10.0.0.2","port":"1","pool_id":"1"}' http://localhost:8080/quantum/v1.0/members/
# curl -X POST -d '{"id":"3","address":"10.0.0.3","port":"1","pool_id":"1"}' http://localhost:8080/quantum/v1.0/members/
# curl -X POST -d '{"id":"4","address":"10.0.0.4","port":"1","pool_id":"1"}' http://localhost:8080/quantum/v1.0/members/
# curl -X POST -d '{"id":"5","address":"10.0.0.5","port":"1","pool_id":"1"}' http://localhost:8080/quantum/v1.0/members/
# curl -X POST -d '{"id":"6","address":"10.0.0.6","port":"1","pool_id":"1"}' http://localhost:8080/quantum/v1.0/members/
# curl -X POST -d '{"id":"7","address":"10.0.0.7","port":"1","pool_id":"1"}' http://localhost:8080/quantum/v1.0/members/
# curl -X POST -d '{"id":"8","address":"10.0.0.8","port":"1","pool_id":"1"}' http://localhost:8080/quantum/v1.0/members/
# curl -X POST -d '{"id":"9","address":"10.0.0.9","port":"1","pool_id":"1"}' http://localhost:8080/quantum/v1.0/members/
# curl -X POST -d '{"id":"10","address":"10.0.0.10","port":"1","pool_id":"1"}' http://localhost:8080/quantum/v1.0/members/

NUM_MEMBERS=$1
curl -X POST -d '{"id":"1","name":"vip1","protocol":"icmp","address":"10.0.0.100","port":"1"}' http://localhost:8080/quantum/v1.0/vips/
curl -X POST -d '{"id":"1","name":"pool1","protocol":"icmp","vip_id":"1"}' http://localhost:8080/quantum/v1.0/pools/
for i in `seq 1 ${NUM_MEMBERS}`; do
 curl -X POST -d '{"id":"'${i}'","address":"10.0.0.'${i}'","port":"1","pool_id":"1"}' http://localhost:8080/quantum/v1.0/members/
done
