import os,time
import subprocess

curr_dir = os.path.dirname(os.path.abspath(__file__))
saved_dir = curr_dir + "/../../systems/hbase/saved_data/24430"
dest_dir = curr_dir + "/../../tests/hbase/24430/"
dest_path = dest_dir + "docker-compose.yml"

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
else:
    os.system("sudo rm -rf " + dest_dir)
    os.makedirs(dest_dir)

container_name = "container_hbase_N1"

os.system("cp -r " + saved_dir + "/* " + dest_dir)
os.system("cp -r " + dest_path + ".old " + dest_path)
os.system("docker-compose -f " + dest_dir + 'docker-compose.yml up -d')

time.sleep(150)
p = subprocess.Popen('docker exec ' + container_name + ' /hbase/bin/hbase pe --nomapred --oneCon=true --valueSize=10 --rows=100 sequentialWrite 1 > ./reproduce_result/log 2>&1', shell=True)
p.wait()

os.system("cp -r " + dest_path + ".new " + dest_path)


os.system("docker-compose -f " + dest_dir + 'docker-compose.yml up -d')
time.sleep(150)

os.system("docker-compose -f " + dest_dir  + 'docker-compose.yml down')

#print("***************************************ERROR and Exception log***************************************")
repo_dir = os.path.join(curr_dir, "..", "reproduce_result", "result")
os.system("rm " + repo_dir)
os.system("sudo grep ERROR -nRi " + dest_dir + " > " + repo_dir)
os.system("sudo grep Exception -nRi " + dest_dir + " >> " + repo_dir)
cmd = "echo \"test_log_dir: " + dest_dir + "\" >> check_result.log"
os.system(cmd)
#print("*****************************************************************************************************")
