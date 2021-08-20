import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import math
import os
import shutil
import utils
import generate_yml


class hiveGenerateYml(generate_yml.generateYml):
    def generate_node_config(self, image, container_name_prefix, node_id, start_interval, num_seeds, is_seed,
                             persistent_dir):
        node_config = """
    DC3N""" + str(node_id + 1) +""":
        container_name: """ + container_name_prefix + "_N" + str(node_id) + """
        image: """ + image + """
        command: bash -c 'sleep 0 && /usr/bin/supervisord'
        networks:
            """ + self.network_name + """:
                ipv4_address:  """ + self.subnet + str(node_id+2) + """
        volumes:
            - """ + persistent_dir + """/persistent/data/n""" + str(node_id+1) + """data:/hive/data
            - """ + persistent_dir + """/persistent/data/n""" + str(node_id+1) + """tmp:/tmp
            - """ + persistent_dir + """/persistent/data/n""" + str(node_id+1) + """log:/hive/logs/
            - """ + persistent_dir + """/persistent/data/n""" + str(node_id+1) + """consolelog:/var/log/supervisor
        environment:
            SERVICE_PRECONDITION: '""" + self.subnet + """2:9870,""" + self.subnet + """2:9000'
        env_file:
            - ./hive.env
        depends_on:
                - DC3N1
        expose:
            - 9083
            - 9000
            - 9870
            - 50010
            - 50020
            - 50070
            - 50075
            - 50090
            - 19888
            - 8188
            - 8020
            - 8030
            - 8031
            - 8032
            - 8033
            - 8040
            - 8042
            - 8088
            - 22        
        """

        return node_config



    # Note that to use generated script, you cannot have conflict services and networks.
    def generate_config(self, version, config, test_name, fname="docker-compose.yml", persistent_dir="."):

        num_nodes = config.num_nodes

        image = utils.get_image_name(version)
        container_name_prefix = utils.get_container_name_prefix(version,test_name)

        self.write_file(fname, self.config_head)

        hdfs_head = """

    DC3N1:
        container_name: container_hdfs_stressTest_N1
        image: image_hdfs_release-2.9.0
        command: bash -c 'sleep 0 && /usr/bin/supervisord'
        networks:
            """ + self.network_name + """:
                ipv4_address:  """ + self.subnet + """2
        volumes:
            - """ + persistent_dir + """/persistent/data/n1data:/tmp
            - """ + persistent_dir + """/persistent/data/n1log:/hadoop/logs/
            - """ + persistent_dir + """/persistent/data/n1consolelog:/var/log/supervisor
        environment:
            SERVICE_PRECONDITION: '""" + self.subnet + """2:9870,""" + self.subnet + """2:9000'
        env_file:
            - ./hive.env
        expose:
            - 9000
            - 9870
            - 50010
            - 50020
            - 50070
            - 50075
            - 50090
            - 19888
            - 8188
            - 8020
            - 8030
            - 8031
            - 8032
            - 8033
            - 8040
            - 8042
            - 8088
            - 22
        
        """
        self.append_file(fname, hdfs_head)

        for i in range(1, num_nodes + 1):
            self.append_file(fname, self.generate_node_config(image, container_name_prefix, i, 0, 1, True,
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


