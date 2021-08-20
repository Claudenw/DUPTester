import sys, os, argparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import generate_yml_cass
import upgrade_path, upgrade_edge


class CassVersion(upgrade_path.Version):
    def generate_yml_wrapper(self, config, test_dir, subnet, test_name, network_name):
        yml_file = test_dir + '/docker-compose.yml'
        generator = generate_yml_cass.cassGenerateYml(subnet, network_name)
        generator.generate_config(self, config, test_name, yml_file, test_dir)
        return yml_file


class CassUpgradeEdge(upgrade_edge.UpgradeEdge):
    def generate_rolling_upgrade_yml(self, config, upgraded_nodes_num, test_dir, subnet, test_name, network_name):
        yml_file = test_dir + '/docker-compose.yml'
        generator = generate_yml_cass.cassGenerateYml(subnet, network_name)
        generator.generate_rolling_upgrade_config(self, config, upgraded_nodes_num, test_name, yml_file, test_dir)
        return yml_file
