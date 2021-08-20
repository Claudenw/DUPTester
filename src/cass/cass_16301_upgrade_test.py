import os,time

curr_dir = os.path.dirname(os.path.abspath(__file__))
saved_dir = curr_dir + "/../../systems/cass/saved_data/16301"
dest_dir = curr_dir + "/../../tests/cass/unittest/cassandra-3.11.6_to_cassandra-4.0-beta3/DefsTest_testUpdateKeyspace/"

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
else:
    os.system("sudo rm -rf " + dest_dir)
    os.makedirs(dest_dir)

os.system("cp -r " + saved_dir + "/* " + dest_dir)
os.system("docker-compose -f " + dest_dir + 'docker-compose.yml up -d')
time.sleep(150)
os.system("docker-compose -f " + dest_dir + 'docker-compose.yml down')

#print("***************************************ERROR and Exception log***************************************")
repo_dir = os.path.join(curr_dir, "..", "reproduce_result", "result")
os.system("rm " + repo_dir)
os.system("sudo grep --text ERROR -nR " + dest_dir + " > " + repo_dir)
os.system("sudo grep --text Exception -nR " + dest_dir + " >> " + repo_dir)
print("test_log_dir: " + dest_dir )
#print("*****************************************************************************************************")
