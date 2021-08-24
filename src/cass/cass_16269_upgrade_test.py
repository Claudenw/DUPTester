import os,time

curr_dir = os.path.dirname(os.path.abspath(__file__))
docker_dir = curr_dir + "/../../systems/cass/saved_data/16269/"
docker_path = docker_dir + "docker-compose.yml"
target_dir = curr_dir + "/../../tests/cass/16269/"
target_path = target_dir + "docker-compose.yml"

if not os.path.exists(target_dir):
    os.makedirs(target_dir)
else:
    os.system("sudo rm -rf " + target_dir)
    os.makedirs(target_dir)

#persistent_path = docker_dir + "persistent/log"

os.system("cp " + docker_path + " " + target_path )

os.system("docker-compose -f " + target_path + " up -d")
time.sleep(60)
#os.system("docker exec container_cass_cassandra-1.1.0_stressTest_N2 /cassandra/tools/bin/stress -d 252.11.1.2,252.11.1.3 -r")
#itime.sleep(20)
os.system("docker-compose -f " + target_path + " down")

#print("***************************************ERROR and Exception log***************************************")
repo_dir = os.path.join(curr_dir, "..", "reproduce_result", "result")
os.system("rm " + repo_dir)
os.system("sudo grep --text ERROR -nR " + target_dir + " > " + repo_dir)
os.system("sudo grep --text Exception -nR " + target_dir + " >> " + repo_dir)
cmd = "echo \"test_log_dir: " + target_dir + "\" >> check_result.log"
os.system(cmd)
#print("*****************************************************************************************************")
