import sys, os, argparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import subprocess, parser, time
import cass_upgrade_path
from cass_config import cassConfig as Config
import utils, upgrade_test_base, upgrade_path


class CassStressingUpgradeTest(upgrade_test_base.UpgradeTestBase):

    def test_old_version(self):
        old_version = self.upgrade_edge.from_version
        old_version_number = old_version.version_number
        new_version_number = self.upgrade_edge.target_version.version_number
        # run stress testing
        container_name = utils.get_container_name_prefix(old_version, self.test_name) + '_N1'
        # note: implicit dependency: ip is hard coded to use one of the nodes in docker-compose.yml
        node_ip = utils.app_name_2_subnet(old_version.application.name) + str(self.test_id) + "." + '2'
        if old_version_number == "cassandra-1.1.0":
            #p = subprocess.Popen('docker exec ' + container_name +
            #                     ' /cassandra/tools/bin/stress -d ' + node_ip + ' -r > tmp 2>&1', shell=True)
            time.sleep(20)
            #p.kill()
        elif old_version_number.find("cassandra-1.2") != -1 or old_version_number.find("cassandra-2.0") != -1:
            #p = subprocess.Popen(['docker', 'exec', container_name,
            #                      '/cassandra/tools/bin/cassandra-stress', '-d', node_ip], cwd=self.test_dir)
            time.sleep(20)
            #p.kill()
        elif new_version_number.find("cassandra-4.") != -1 and old_version_number.find("cassandra-3.11.4") == -1:
            p = subprocess.Popen("docker exec " + container_name + " /cassandra/tools/bin/cassandra-stress user "
                                                        "profile=/cassandra/tools/cqlstress-example.yaml ops\("
                                                        "insert=3\) no-warmup cl=QUORUM -node " + node_ip + " > tmp 2>&1", shell=True)
            time.sleep(4)
            p.kill()
        else:
            p = subprocess.Popen('docker exec ' + container_name +
                                  ' /cassandra/tools/bin/cassandra-stress write n=300 ' +
                                  '-node ' +  node_ip + " > tmp 2>&1", shell=True)
            p.wait()
        # if we are using a stress testing tool that needs to be killed
        # p.kill()

    def test_new_version(self, test_node_id, is_rolling_upgrade=False):
        # read and check compatibility
        new_version = self.upgrade_edge.target_version
        new_version_number = new_version.version_number
        old_version = self.upgrade_edge.from_version
        if is_rolling_upgrade and test_node_id == 1:
            container_name = utils.get_container_name_prefix(old_version, self.test_name) + '_N' + str(test_node_id)
            version_number = self.upgrade_edge.from_version.version_number
        else:
            version_number = new_version.version_number
            container_name = utils.get_container_name_prefix(new_version, self.test_name) + '_N' + str(test_node_id)
        node_ip = utils.app_name_2_subnet(old_version.application.name) + str(self.test_id) + "." + str(
            test_node_id + 1)


        if version_number == "cassandra-1.1.0":

            p = subprocess.Popen('docker exec ' + container_name +
                                 ' /cassandra/tools/bin/stress -d ' + node_ip + ' -r >> tmp 2>&1', shell=True)
            time.sleep(20)
            p.kill()
            p = subprocess.Popen('docker exec ' + container_name +
                                 ' /cassandra/tools/bin/stress -d ' + node_ip + ' -o read >> tmp 2>&1',
                                 shell=True)
            time.sleep(20)
            p.kill()
        elif version_number.find("cassandra-1.2") != -1 or version_number.find("cassandra-2.0") != -1:

            p = subprocess.Popen('docker exec ' + container_name +
                                 ' /cassandra/tools/bin/cassandra-stress -d ' + node_ip + ' >> tmp 2>&1', shell=True)

            time.sleep(20)
            p.kill()

            p = subprocess.Popen('docker exec ' + container_name +
                                 ' /cassandra/tools/bin/cassandra-stress -d ' + node_ip + ' -o read >> tmp 2>&1',
                                 shell=True)
            time.sleep(20)
            p.kill()
        elif new_version_number.find("cassandra-4.") != -1 or new_version_number.find("cassandra-4") != -1:
            p = subprocess.Popen("docker exec " + container_name + " /cassandra/tools/bin/cassandra-stress user "
                                                        "profile=/cassandra/tools/cqlstress-example.yaml ops\("
                                                        "insert=3\) no-warmup cl=QUORUM -node " + node_ip + " >> tmp 2>&1", shell=True)
            time.sleep(4)
            p.kill()
            p = subprocess.Popen("docker exec " + container_name + " /cassandra/tools/bin/cassandra-stress user "
                                                        "profile=/cassandra/tools/cqlstress-example.yaml ops\("
                                                        "simple1=1\) no-warmup cl=QUORUM -node " + node_ip + " >> tmp 2>&1", shell=True)
            time.sleep(4)
            p.kill()

        else:
            p = subprocess.Popen('docker exec ' + container_name +
                                 ' /cassandra/tools/bin/cassandra-stress write n=30 -node ' +
                                 node_ip + ' >> tmp 2>&1', shell=True)
            p.wait()

            p = subprocess.Popen('docker exec ' + container_name +
                                 ' /cassandra/tools/bin/cassandra-stress read n=30 -node ' +
                                 node_ip + ' >> tmp 2>&1', shell=True)
            p.wait()

        if is_rolling_upgrade and (test_node_id == 1 or test_node_id == 2):
            if test_node_id == 1:
                id = 2
            else:
                id = 1
            container_name = utils.get_container_name_prefix(new_version, self.test_name) + '_N' + str(id)
            node_ip = utils.app_name_2_subnet(old_version.application.name) + str(self.test_id) + "." + str(id+1)
            new_version_number = new_version.version_number

            if new_version_number == "cassandra-1.1.0":
                p = subprocess.Popen('docker exec ' + container_name +
                                     ' /cassandra/tools/bin/stress -d ' + node_ip + ' -r >> tmp 2>&1', shell=True)
                time.sleep(20)
                p.kill()
                p = subprocess.Popen('docker exec ' + container_name +
                                     ' /cassandra/tools/bin/stress -d ' + node_ip + ' -o read >> tmp 2>&1',
                                     shell=True)
                time.sleep(20)
                p.kill()
            elif new_version_number.find("cassandra-1.2") != -1 or new_version_number.find("cassandra-2.0") != -1:
                nodes_pre = utils.app_name_2_subnet(old_version.application.name) + str(self.test_id)
                nodes = ""
                for i in range(2, self.config.num_nodes + 2):
                    nodes += nodes_pre + "." + str(i) + ","
                print(nodes)
                p = subprocess.Popen('docker exec ' + container_name +
                                      ' /cassandra/tools/bin/cassandra-stress -d ' + nodes[:-1] + ' -r >> tmp 2>&1', shell=True)
                time.sleep(20)
                p.kill()
                p = subprocess.Popen('docker exec ' + container_name +
                                      ' /cassandra/tools/bin/cassandra-stress -d ' + node_ip + ' -o read >> tmp 2>&1', shell=True)
                time.sleep(20)
                p.kill()
            elif new_version_number.find("cassandra-4.") != -1 or new_version_number.find("cassandra-4") != -1:
                p = subprocess.Popen("docker exec " + container_name + " /cassandra/tools/bin/cassandra-stress user "
                                                                       "profile=/cassandra/tools/cqlstress-example.yaml ops\("
                                                                       "insert=3\) no-warmup cl=QUORUM -node " + node_ip + " >> tmp 2>&1", shell=True)
                time.sleep(4)
                p.kill()
                p = subprocess.Popen("docker exec " + container_name + " /cassandra/tools/bin/cassandra-stress user "
                                                                       "profile=/cassandra/tools/cqlstress-example.yaml ops\("
                                                                       "simple1=1\) no-warmup cl=QUORUM -node " + node_ip + " >> tmp 2>&1", shell=True)
                time.sleep(4)
                p.kill()
            else:
                p = subprocess.Popen('docker exec ' + container_name +
                                   ' /cassandra/tools/bin/cassandra-stress write n=30 -node ' +
                                     node_ip + ' >> tmp 2>&1', shell=True)
                p.wait()
                
                p = subprocess.Popen('docker exec ' + container_name +
                                 ' /cassandra/tools/bin/cassandra-stress read n=30 -node ' +
                                 node_ip + ' >> tmp 2>&1', shell=True)
                p.wait()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate yml file required to start a docker compose cluster.',
                                     epilog='Example usage: python generate-yml.py 5 docker-compose.yml test -s 2')

    parser.add_argument("from_version", help="from version")
    parser.add_argument("target_version", help="target version")
    parser.add_argument("-n", "--nodes", default=3, help="number of seeds", type=int)
    parser.add_argument("-s", "--seeds", default=1, help="number of seeds", type=int)
    parser.add_argument("-r", "--isRollingUpgrade", action="store_true", default=False,
                        help="the parent dir of the persistent data, default is the current dir")

    args = parser.parse_args()

    old_version = cass_upgrade_path.CassVersion("cassandra", args.from_version)
    new_version = cass_upgrade_path.CassVersion("cassandra", args.target_version)
    config = Config(args.nodes, args.seeds)
    application_start_interval = 150
    upgrade_edge = cass_upgrade_path.CassUpgradeEdge(old_version, new_version)

    test = CassStressingUpgradeTest(upgrade_edge, config, application_start_interval, "stress", "stressTest")

    if args.isRollingUpgrade:
        if config.num_nodes > 1 and config.num_seeds > 0:
            test.test_rolling_upgrade()
        else:
            print("WARN: To perform rolling upgrade, num_nodes > 1 and num_seeds > 0 is required! ")
    else:
        test.test_upgrade()


