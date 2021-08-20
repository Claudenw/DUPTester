import os,time
import subprocess

curr_dir = os.path.dirname(os.path.abspath(__file__))
saved_dir = curr_dir + "/../../systems/kafka/saved_data/10041"
dest_dir = curr_dir + "/../../tests/kafka/10041/"
dest_path = dest_dir + "docker-compose.yml"

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
else:
    os.system("sudo rm -rf " + dest_dir)
    os.makedirs(dest_dir)

container_name = "container_kafka_N1"

os.system("cp -r " + saved_dir + "/* " + dest_dir)
os.system("cp -r " + dest_path + ".old " + dest_path)
os.system("docker-compose -f " + dest_dir + 'docker-compose.yml up -d')

time.sleep(150)

p = subprocess.Popen('docker exec ' + container_name +
                              ' kafka/bin/kafka-producer-perf-test.sh --topic test --num-records 500 ' +
                              '--record-size 300 --throughput 100 --producer-props ' +
                              'bootstrap.servers=252.12.1.2:9092 > ./reproduce_result/log 2>&1', shell=True)
p.wait()
p = subprocess.Popen('docker exec ' + container_name +
                              ' kafka/bin/kafka-consumer-perf-test.sh --topic test ' +
                              '--broker-list 252.12.1.2:9092 ' +
                              '--messages 500 --threads 1 >> ./reproduce_result/log 2>&1', shell=True)
p.wait()

os.system("cp -r " + dest_path + ".new " + dest_path)

os.system("docker-compose -f " + dest_dir + 'docker-compose.yml up -d')
time.sleep(150)

p = subprocess.Popen('docker exec ' + container_name +
                              ' kafka/bin/kafka-consumer-perf-test.sh --topic test ' +
                              '--broker-list 252.12.1.2:9092 ' +
                              '--messages 500 --threads 1 >> ./reproduce_result/log 2>&1', shell=True)
p.wait()

os.system("docker-compose -f " + dest_dir  + 'docker-compose.yml down')

#print("***************************************ERROR and Exception log***************************************")
curr_dir = os.path.dirname(os.path.abspath(__file__))
repo_dir = os.path.join(curr_dir, "..", "reproduce_result", "result")
os.system("rm " + repo_dir)
os.system("sudo grep ERROR -nR " + dest_dir + " > " + repo_dir)
os.system("sudo grep Exception -nR " + dest_dir + " >> " + repo_dir)
print("test_log_dir: " + dest_dir )
#print("*****************************************************************************************************")
