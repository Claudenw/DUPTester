import subprocess
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import generate_yml_hive
import upgrade_path, upgrade_edge, utils

curr_dir = os.path.dirname(os.path.abspath(__file__))

class HiveVersion(upgrade_path.Version):
    def generate_yml_wrapper(self, config, test_dir, subnet,test_name, network_name):
        yml_file = test_dir + '/docker-compose.yml'
        env_file = curr_dir + "/../../systems/hive/template/build-image/hive.env"
        os.system("cp " + env_file + " " + test_dir)
        generator = generate_yml_hive.hiveGenerateYml(subnet,network_name)
        generator.generate_config(self, config, test_name, yml_file, test_dir)
        return yml_file


class HiveUpgradeEdge(upgrade_edge.UpgradeEdge):

    # TODO: rolling upgrade
    def rolling_upgrade(self, config, upgraded_nodes_num, test_dir, subnet, test_name, network_name):
        print("Hive rolling upgrade test is not available.")
        return yml_file

