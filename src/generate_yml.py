class generateYml():
    def __init__(self, subnet, network_name, node_name_prefix="DC3N"):
        self.config_head = """
version: '3'

services:
"""
        self.subnet = subnet
        self.node_name_prefix = node_name_prefix
        self.network_name = network_name

    def generate_node_config(self):
        pass

    def generate_config_tail(self, network_mask):
        config_tail = """
networks:
    """+ self.network_name +""":
        driver: bridge
        ipam:
            driver: default
            config:
                - subnet: """ + self.subnet + """1/24
        """
        return config_tail

    def write_file(self, fname, string):
        with open(fname, 'w') as out:
            out.write(string)

    def append_file(self, fname, string):
        with open(fname, 'a') as out:
            out.write(string)

    def generate_config(self, version, config, test_name, fname="docker-compose.yml", persistent_dir="."):
        pass

    def generate_rolling_upgrade_config(self, upgrade_edge, config, upgraded_nodes_num, test_name, fname="docker-compose.yml",
                                        persistent_dir="."):
        pass
