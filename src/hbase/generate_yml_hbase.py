import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import math
import os
import shutil
import utils
import generate_yml


class hbaseGenerateYml(generate_yml.generateYml):
    def generate_node_config(self, image, container_name_prefix, node_id, start_interval, num_seeds, is_seed,
                             persistent_dir):

        seed_depends = ""
        node_name = ""
        if is_seed:
            node_name = "hbase-master" + str(node_id)
            seed_depends = """
        ports:
            - 16000:16000
            - 16010:16010
        depends_on:
            - zookeeper
            """
        else :
            node_name = "hbase-regionserver" + str(node_id)
            seed_depends = """
        ports:
            - 1603""" + str(node_id-2) + """:16030
            - 1620""" + str(node_id-1) + """:16201
            - 1630""" + str(node_id-1) + """:16301
        depends_on:
            - zookeeper"""
            for i in range(1, num_seeds + 1):
                seed_depends = seed_depends + """
            - hbase-master""" +str(i) + """
            """

        node_config = """
    """ + node_name + """:
        container_name: container_hbase_N""" + str(node_id) + """
        image: """ + image + """
        command: bash -c 'sleep """ + str(start_interval) + """ && /usr/bin/supervisord'
        networks:
            """ + self.network_name + """:
                ipv4_address: """ + self.subnet + str(node_id+1) + """
        volumes:
            - """ + persistent_dir + """/persistent/data/n""" + str(node_id) + """data/hbase:/var/lib/hbase
            - """ + persistent_dir + """/persistent/data/n""" + str(node_id) + """data/zookeeper:/var/lib/zookeeper
            - """ + persistent_dir + """/persistent/log/n""" + str(node_id) + """log:/hbase/logs/
            - """ + persistent_dir + """/persistent/consolelog/n""" + str(node_id) + """consolelog:/var/log/supervisor
            - """ + persistent_dir + """/persistent/tmp/n""" + str(node_id) + """tmp:/tmp""" + seed_depends

        return node_config



    # Note that to use generated script, you cannot have conflict services and networks.
    def generate_config(self, version, config, test_name, fname="docker-compose.yml", persistent_dir="."):

        num_nodes = config.num_nodes
        num_seeds = config.num_seeds

        image = utils.get_image_name(version)
        container_name_prefix = utils.get_container_name_prefix(version,test_name)

        if num_seeds is None:
            num_seeds = 1

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


        zookeeper_tail = """
    zookeeper:
        image: image_zk_branch-3.6
        command: bash -c 'sleep 0 && /usr/bin/supervisord'
        volumes:
            - """ + persistent_dir + """/persistent/data/zkdata:/tmp/zookeeper
            - """ + persistent_dir + """/persistent/log/zklog:/var/log/supervisor
        restart: always
        networks:
            """ + self.network_name + """:
                ipv4_address: """ + self.subnet + """5
        ports:
            - 2181:2181
        environment:
            ZOO_MY_ID: 1
        expose:
            - 2181
            - 2888
            - 3888
            - 8080
        """
        self.append_file(fname, zookeeper_tail)

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


