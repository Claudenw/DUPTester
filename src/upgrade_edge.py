import os
import subprocess
import utils


class UpgradeEdge:
    def __init__(self, from_version, target_version):
        self.from_version = from_version
        self.target_version = target_version

    def rolling_upgrade(self,config, upgraded_nodes_num, test_dir, subnet, test_name, network_name):
        yml_file = self.generate_rolling_upgrade_yml(config, upgraded_nodes_num, test_dir, subnet, test_name, network_name)
        os.system("docker-compose -f " + yml_file + " up -d")
        return yml_file

    def generate_rolling_upgrade_yml(self, config, upgraded_nodes_num, test_dir, subnet, test_name, network_name):
        pass
