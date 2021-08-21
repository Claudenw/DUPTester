import sys, os, argparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import subprocess
import hbase_upgrade_path
import time
import utils, upgrade_path, upgrade_test_base
from hbase_config import hbaseConfig as Config


class HbaseStressingUpgradeTest(upgrade_test_base.UpgradeTestBase):

    def test_old_version(self):
        old_version = self.upgrade_edge.from_version
        # run stress testing
        main_container_name = 'container_hbase_N1'
        container_name = 'container_hbase_N'
        for i in range(1, self.config.num_nodes + 1):
            p = subprocess.Popen('docker exec ' + container_name + str(i) + ' bash /hbase/bin/start-hbase.sh > ./reproduce_result/log 2>&1', shell=True)
            p.wait()

        time.sleep(20)
        if old_version.version_number.find("2.0") != -1 or old_version.version_number.find("2.1") != -1:
            for i in range(1, self.config.num_nodes + 1):
                p = subprocess.Popen('docker exec ' + container_name + str(i) + ' rm -rf /tmp/hbase-root >> ./reproduce_result/log 2>&1', shell=True)
                p.wait()
            for i in range(1, self.config.num_nodes + 1):
                p = subprocess.Popen('docker exec ' + container_name + str(i) + ' bash /hbase/bin/start-hbase.sh >> ./reproduce_result/log 2>&1', shell=True)
                p.wait()
        time.sleep(80)
        # note: implicit dependency: ip is hard coded to use one of the nodes in docker-compose.yml
        p = subprocess.Popen('docker exec ' + main_container_name +
                             ' /hbase/bin/hbase pe --nomapred --oneCon=true --valueSize=10 --rows=100 sequentialWrite 1 >> ./reproduce_result/log 2>&1', shell=True)
        p.wait()

        if self.upgrade_edge.target_version.version_number.find("2.2.") != -1:
            p = subprocess.Popen('docker exec ' + main_container_name +
                                  ' bash /hbase/bin/stop-hbase.sh >> ./reproduce_result/log 2>&1', shell=True)
            p.wait()

            string = """ <property>
    <name>hbase.procedure.upgrade-to-2-2</name>
    <value>true</value>
 </property>"""
            for node_id in range(1, self.config.num_nodes + 1):
                container_name = 'container_hbase_N' + str(node_id)
                p = subprocess.Popen(['docker', 'exec', container_name,
                                      'echo', string, ">>" "/hbase/config/hbase-site.xml"], cwd=self.test_dir)
                p.wait()

            p = subprocess.Popen('docker exec ' + main_container_name +
                                  ' bash /hbase/bin/start-hbase.sh >> ./reproduce_result/log 2>&1', shell=True)
            p.wait()

        else:
            for node_id in range(1, self.config.num_nodes + 1):
                container_name = 'container_hbase_N' + str(node_id)
                p = subprocess.Popen('docker exec ' + container_name +
                                      ' bash /hbase/bin/graceful_stop.sh regionservers >> ./reproduce_result/log 2>&1', shell=True)
                p.wait()
            for node_id in range(1, self.config.num_nodes + 1):
                container_name = 'container_hbase_N' + str(node_id)
                p = subprocess.Popen('docker exec ' + container_name +
                                      ' bash /hbase/bin/rolling-restart.sh >> ./reproduce_result/log 2>&1', shell=True)

            p.wait()

    def test_new_version(self, test_node_id, is_rolling_upgrade=False):
        # read and check compatibility
        new_version = self.upgrade_edge.target_version
        container_name = 'container_hbase_N'
        for i in range(1, self.config.num_nodes + 1):
            p = subprocess.Popen('docker exec ' + container_name + str(i) + ' bash /hbase/bin/start-hbase.sh >> ./reproduce_result/log 2>&1', shell=True)
            p.wait()
        '''
        time.sleep(20)
        if new_version.version_number.find("2.0") != -1 or new_version.version_number.find("2.1") != -1:
            for i in range(1, self.config.num_nodes + 1):
                p = subprocess.Popen('docker exec ' + container_name + str(i) + ' rm -rf /tmp/hbase-root >> ./reproduce_result/log 2>&1', shell=True)
                p.wait()
        '''
        time.sleep(80)

        container_name = 'container_hbase_N1'

        p = subprocess.Popen('docker exec ' + container_name +
                             ' /hbase/bin/hbase pe --nomapred --oneCon=true --valueSize=10 --rows=100 randomRead 1 >> ./reproduce_result/log 2>&1', shell=True)
        time.sleep(120)
        p.kill()



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Generate yml file required to start a docker compose cluster.',
         epilog='Example usage: python generate-yml.py 5 docker-compose.yml test -s 2')

    parser.add_argument("from_version", help="from version")
    parser.add_argument("target_version", help="target version")
    parser.add_argument("-n", "--nodes", default = 3,  help="number of seeds", type=int)
    parser.add_argument("-s", "--seeds", default = 1, help="number of seeds", type=int)
    parser.add_argument("-r", "--isRollingUpgrade", action="store_true", default = False, help="the parent dir of the persistent data, default is the current dir")

    args = parser.parse_args()

    old_version = hbase_upgrade_path.HbaseVersion("hbase", args.from_version)
    new_version = hbase_upgrade_path.HbaseVersion("hbase", args.target_version)
    config = Config(args.nodes, args.seeds)
    application_start_interval = 20
    upgrade_edge = hbase_upgrade_path.HbaseUpgradeEdge(old_version, new_version)

    test = HbaseStressingUpgradeTest(upgrade_edge, config, application_start_interval, "stress", "stressTest")

    if args.isRollingUpgrade:
        test.test_rolling_upgrade()
    else:
        test.test_upgrade()
