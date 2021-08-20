import sys, os, argparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import subprocess
import generate_yml_hbase
import upgrade_path, upgrade_edge, utils


class HbaseVersion(upgrade_path.Version):
    def generate_yml_wrapper(self, config, test_dir, subnet,test_name, network_name):
        yml_file = test_dir + '/docker-compose.yml'
        generator = generate_yml_hbase.hbaseGenerateYml(subnet,network_name)
        generator.generate_config(self, config, test_name, yml_file, test_dir)
        return yml_file


class HbaseUpgradeEdge(upgrade_edge.UpgradeEdge):

    # TODO: rolling upgrade
    def rolling_upgrade(self, config, upgraded_nodes_num, test_dir, subnet, test_name, network_name):
        print("Hbase rolling upgrade test is not available.")
        yml_file = test_dir + '/docker-compose.yml'
        return yml_file

