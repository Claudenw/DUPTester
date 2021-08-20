# Taking an upgrade path, perform upgrade and test.
# All upgrade tests extend this class and override its test methods.
# TODO: It only supports testing upgrading btw. 2 versions.
#       We should further support upgrading through an upgrade path involving more than 2 versions.

# import upgrade_path

import time
import os
import utils

class UpgradeTestBase:

    def __init__(self, upgrade_edge, config, application_start_interval, test_type, test_name, test_id = 1):
        self.upgrade_edge = upgrade_edge
        self.config = config
        self.application_start_interval = application_start_interval
        self.test_type = test_type
        self.test_name = test_name
        self.test_dir = utils.get_test_dir(self.upgrade_edge, self.test_type, self.test_name)
        self.docker_console_log = self.test_dir + "/docker_console.log"
        self.test_id = test_id


    def test_upgrade(self):

        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
            #print("If you want to run this test again, remember to clean previous test data.")
        else:
            #print("WARN: " + self.test_dir + "exists! Previous test data might not have been cleaned.\n")
            os.system("sudo rm -rf " + self.test_dir)
            os.makedirs(self.test_dir)
        print("Test data is stored in " + self.test_dir )

        yml_file = self.upgrade_edge.from_version.start_cluster(self.config, self.test_dir, self.upgrade_edge, self.test_name, self.test_id)

        time.sleep(self.application_start_interval) # wait a while for the cluster to start
        # e.g., stress testing

        try:
            self.test_old_version()
            #time.sleep(60)
        except Exception as e:
            print("ERROR INFO: " + str(e))
            pass

        self.upgrade_edge.from_version.teardown_cluster(yml_file, self.test_dir, self.docker_console_log, self.config)

        yml_file = self.upgrade_edge.target_version.start_cluster(self.config, self.test_dir, self.upgrade_edge, self.test_name, self.test_id)

        time.sleep(self.application_start_interval)
        # e.g., read and check

        try:
            self.test_new_version(1)
        except Exception as e:
            print("ERROR INFO: " + str(e))
            pass

        self.upgrade_edge.target_version.teardown_cluster(yml_file, self.test_dir, self.docker_console_log, self.config)

        curr_dir = os.path.dirname(os.path.abspath(__file__))
        repo_dir = os.path.join(curr_dir, "reproduce_result", "result")
        os.system("rm " + repo_dir)
        os.system("sudo grep ERROR -nR " + self.test_dir + " > " + repo_dir )
        os.system("sudo grep Exception -nR " + self.test_dir + " >> " + repo_dir)
        print("********************test_log_dir: " + self.test_dir )

    def test_rolling_upgrade(self):

        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
            print("Test data is stored in " + self.test_dir )
            print("If you want to run this test again, remember to clean previous test data.")
        else:
            print("WARN: " + self.test_dir + "exists! Previous test data might not have been cleaned.")
            os.system("sudo rm -rf " + self.test_dir)

        yml_file = self.upgrade_edge.from_version.start_cluster(self.config, self.test_dir, self.upgrade_edge, self.test_name, self.test_id)

        time.sleep(self.application_start_interval)
        # e.g., stress testing
        try:
            self.test_old_version()
            #time.sleep(60)
        except Exception as e:
            print("ERROR INFO: " + str(e))
            pass


        curr_dir = os.path.dirname(os.path.abspath(__file__))
        repo_dir = os.path.join(curr_dir, "reproduce_result", "result")
        os.system("rm " + repo_dir)
        for upgraded_nodes_num in range(1, self.config.num_nodes + 1):
            subnet =utils.app_name_2_subnet(self.upgrade_edge.from_version.application.name) + str(self.test_id) + "."
            network_name = utils.get_network_name(self.upgrade_edge, self.test_name)
            #config, upgraded_nodes_num, test_dir, subnet, test_name, network_name
            yml_file = self.upgrade_edge.rolling_upgrade(self.config, upgraded_nodes_num, self.test_dir, subnet,self.test_name, network_name )
            # e.g., read and check
            time.sleep(self.application_start_interval)
            try:
                self.test_new_version(upgraded_nodes_num, True)
                os.system("sudo grep ERROR -nR " + self.test_dir + " >> " + repo_dir)
                os.system("sudo grep Exception -nR " + self.test_dir + " >> " + repo_dir)
            except Exception as e:
                print("ERROR INFO: " + str(e))
                pass

        self.upgrade_edge.target_version.teardown_cluster(yml_file, self.test_dir, self.docker_console_log, self.config)

        print("**************test_log_dir: " + self.test_dir)

    def test_old_version(self):
        pass

    def test_new_version(self, test_node_id, is_rolling_upgrade):
        pass
