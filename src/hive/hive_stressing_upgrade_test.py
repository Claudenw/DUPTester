import sys, os, argparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import subprocess
import hive_upgrade_path
import time
import utils, upgrade_path, upgrade_test_base
from hive_config import hiveConfig as Config


class HiveStressingUpgradeTest(upgrade_test_base.UpgradeTestBase):

    def test_old_version(self):
        old_version = self.upgrade_edge.from_version
        # run stress testing
        container_name = utils.get_container_name_prefix(old_version,"stressTest") + '_N1'
        # note: implicit dependency: ip is hard coded to use one of the nodes in docker-compose.yml
        p = subprocess.Popen('docker exec ' + container_name + ' bash data_create.sh > ./reproduce_result/log 2>&1', shell=True)
        p.wait()
        time.sleep(30)


    def test_new_version(self, test_node_id, is_rolling_upgrade=False):
        # read and check compatibility
        new_version = self.upgrade_edge.target_version
        container_name = utils.get_container_name_prefix(new_version,"stressTest") + '_N1'
        p = subprocess.Popen('docker exec ' + container_name + ' bash remove_dbex.sh >> ./reproduce_result/log 2>&1', shell=True)
        p.wait(30)
        if new_version.version_number == "2.3.7":
            time.sleep(100)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Generate yml file required to start a docker compose cluster.',
         epilog='Example usage: python generate-yml.py 5 docker-compose.yml test -s 2')

    parser.add_argument("from_version", help="from version")
    parser.add_argument("target_version", help="target version")
    parser.add_argument("-n", "--nodes", default = 3,  help="number of seeds", type=int)
    parser.add_argument("-s", "--seeds", default = 1, help="number of seeds", type=int)
    parser.add_argument("-r", "--isRollingUpgrade", action="store_true", default = False, help="the parent dir of the persistent data, default is the current dir")

    args = parser.parse_args()

    old_version = hive_upgrade_path.HiveVersion("hive", args.from_version)
    new_version = hive_upgrade_path.HiveVersion("hive", args.target_version)
    config = Config(args.nodes)
    application_start_interval = 60
    upgrade_edge = hive_upgrade_path.HiveUpgradeEdge(old_version, new_version)
    
    test = HiveStressingUpgradeTest(upgrade_edge, config, application_start_interval, "stress", "stressTest")

    if args.isRollingUpgrade:
        test.test_rolling_upgrade()
    else:
        test.test_upgrade()



