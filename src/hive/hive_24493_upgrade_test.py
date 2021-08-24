import os,time
import subprocess

curr_dir = os.path.dirname(os.path.abspath(__file__))
saved_dir = curr_dir + "/../../systems/hive/saved_data/24493"
dest_dir = curr_dir + "/../../tests/hive/24493/"
dest_path = dest_dir + "docker-compose.yml"

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
else:
    os.system("sudo rm -rf " + dest_dir)
    os.makedirs(dest_dir)

container_name = "container_hive_2.1.1_stressTest_N1"

os.system("cp -r " + saved_dir + "/* " + dest_dir)
os.system("cp -r " + dest_path + ".old " + dest_path)

os.system("docker-compose -f " + dest_dir + 'docker-compose.yml up -d')

time.sleep(60)
p = subprocess.Popen('docker exec ' + container_name + ' bash data_create.sh > ./reproduce_result/log 2>&1', shell=True)
p.wait()

os.system("cp -r " + dest_path + ".new " + dest_path)


container_name = "container_hive_2.3.7_stressTest_N1"
os.system("docker-compose -f " + dest_dir + 'docker-compose.yml up -d')
time.sleep(60)

p = subprocess.Popen('docker exec ' + container_name + ' bash remove_dbex.sh >> ./reproduce_result/log 2>&1', shell=True)
p.wait()
time.sleep(100)

os.system("docker-compose -f " + dest_dir + 'docker-compose.yml down')


#print("***************************************ERROR and Exception log***************************************")
repo_dir = os.path.join(curr_dir, "..", "reproduce_result", "result")
os.system("rm " + repo_dir)
os.system("sudo grep ERROR -nR " + dest_dir + " > " + repo_dir)
os.system("sudo grep Exception -nR " + dest_dir + " >> " + repo_dir)
cmd = "echo \"test_log_dir: " + dest_dir + "\" >> check_result.log"
os.system(cmd)
#print("*****************************************************************************************************")
