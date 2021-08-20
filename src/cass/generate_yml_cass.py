import sys, os, argparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import math
import utils
import generate_yml


class cassGenerateYml(generate_yml.generateYml):

    def generate_node_config(self, image, container_name_prefix, node_id, start_interval, num_seeds, is_seed,
                             persistent_dir):
        seed_config = """
            - CASSANDRA_SEEDS="""
        for i in range(2, num_seeds + 2):
            seed_config = seed_config + self.subnet + str(i) + ","

        seed_depends = ""
        if not is_seed:
            seed_depends = """
        depends_on:"""
            for i in range(1, num_seeds + 1):
                seed_depends = seed_depends + """
                - """ + self.node_name_prefix + str(i)

        node_config = """
    DC3N""" + str(node_id) + """:
        container_name: """ + container_name_prefix + "_N" + str(node_id) + """
        image: """ + image + """
        command: bash -c 'sleep """ + str(start_interval) + """ && /usr/bin/supervisord'
        networks:
            """ + self.network_name + """:
                ipv4_address: """+ self.subnet + str(node_id+1) + """
        volumes:
            - """ + persistent_dir + """/persistent/data/n""" + str(node_id) + """data:/var/lib/cassandra
            - """ + persistent_dir + """/persistent/log/n""" + str(node_id) + """log:/var/log/cassandra
            - """ + persistent_dir + """/persistent/consolelog/n""" + str(node_id) + """consolelog:/var/log/supervisor
        environment:
            - CASSANDRA_CONFIG=/cassandra/conf
            - CASSANDRA_CLUSTER_NAME=dev_cluster""" + seed_config + """
            - CASSANDRA_LOGGING_LEVEL=DEBUG""" + seed_depends + """
        expose:
            - 7000
            - 7001
            - 7199
            - 9042
            - 9160
        ulimits:
            memlock: -1
            nproc: 32768
            nofile: 100000
        """
        return node_config

    # Note that to use generated script, you cannot have conflict services and networks.
    def generate_config(self, version, config, test_name, fname="docker-compose.yml", persistent_dir="."):
        num_nodes = config.num_nodes
        num_seeds = config.num_seeds

        image = utils.get_image_name(version)
        container_name_prefix = utils.get_container_name_prefix(version, test_name)
        if num_seeds is None:
            if num_nodes <= 2:
                num_seeds = 1
            else:
                num_seeds = 2

        assert num_seeds <= num_nodes

        self.write_file(fname, self.config_head)

        for i in range(1, num_seeds + 1):
            self.append_file(fname, self.generate_node_config(image, container_name_prefix, i, 0, num_seeds, True,
                                                              persistent_dir))

        for i in range(num_seeds + 1, num_nodes + 1):
            self.append_file(fname, self.generate_node_config(image, container_name_prefix, i, 0, num_seeds, False,
                                                              persistent_dir))

        network_mask = int(math.ceil(math.log(num_nodes + 1, 2)))
        if network_mask < 2:  # network mask has to be >= 2
            network_mask = 2
        self.append_file(fname, self.generate_config_tail(network_mask))

    def generate_rolling_upgrade_config(self, upgrade_edge, config, upgraded_nodes_num, test_name, fname="docker-compose.yml",
                                        persistent_dir="."):
        num_nodes = config.num_nodes
        num_seeds = config.num_seeds

        old_image = utils.get_image_name(upgrade_edge.from_version)
        new_image = utils.get_image_name(upgrade_edge.target_version)
        old_container_name_prefix = utils.get_container_name_prefix(upgrade_edge.from_version, test_name)
        new_container_name_prefix = utils.get_container_name_prefix(upgrade_edge.target_version, test_name)

        if num_seeds is None:
            if num_nodes <= 2:
                num_seeds = 1
            else:
                num_seeds = 2

        assert num_seeds <= num_nodes

        self.write_file(fname, self.config_head)

        start_node = 1

        if num_seeds == 1:
            if upgraded_nodes_num == 1:
                start_node = 2
                self.append_file(fname, self.generate_node_config(old_image, old_container_name_prefix, 1, 0, num_seeds,
                                                                  True, persistent_dir))
                self.append_file(fname,
                                 self.generate_node_config(new_image, new_container_name_prefix, 2, 0, num_seeds, False,
                                                           persistent_dir))
        if start_node < num_seeds + 1:
            for i in range(start_node, num_seeds + 1):
                if i > upgraded_nodes_num:
                    self.append_file(fname, self.generate_node_config(old_image, old_container_name_prefix, i, 0, num_seeds,
                                                                  True, persistent_dir))
                else:
                    self.append_file(fname, self.generate_node_config(new_image, new_container_name_prefix, i, 0, num_seeds,
                                                                  True, persistent_dir))
        if start_node > num_seeds:
            start_node_id = start_node
        else:
            start_node_id = num_seeds

        for i in range(start_node_id + 1, num_nodes + 1):
            if i > upgraded_nodes_num:
                self.append_file(fname,
                                 self.generate_node_config(old_image, old_container_name_prefix, i, 0, num_seeds, False,
                                                           persistent_dir))
            else:
                self.append_file(fname,
                                 self.generate_node_config(new_image, new_container_name_prefix, i, 0, num_seeds, False,
                                                           persistent_dir))

        network_mask = int(math.ceil(math.log(num_nodes + 1, 2)))
        if network_mask < 2:  # network mask has to be >= 2
            network_mask = 2
        self.append_file(fname, self.generate_config_tail(network_mask))

# if __name__ == '__main__':
#
#     parser = argparse.ArgumentParser(description='Generate yml file required to start a docker compose cluster.',
#         epilog='Example usage: python generate-yml.py 5 docker-compose.yml test -s 2')
#
#     parser.add_argument("num_nodes", help="number of nodes", type=int)
#     parser.add_argument("-s", "--seeds", help="number of seeds", type=int)
#     parser.add_argument("-p", "--persistent", help="the parent dir of the persistent data, default is the current dir")
#     parser.add_argument("yml", help="file name of generated yml file")
#     parser.add_argument("image", help="name of container image")
#
#     args = parser.parse_args()
#     assert args.num_nodes > 0
#
#     generate_config(args.image, args.num_nodes, args.yml, args.seeds)

