import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import hbase_upgrade_path
import utils

class HbaseBuildImage():

    def build_image(self, abbr, application, version_commit, version_number, num_node, force):

        version = hbase_upgrade_path.HbaseVersion(application, version_number)
        curr_dir = os.path.dirname(os.path.abspath(__file__))

        # the target path and the template path which the files should copy from
        target_path = curr_dir + '/../../systems/' + abbr + '/' + version_number
        template_path = curr_dir + '/../../systems/' + abbr + '/template'


        #create the directory and copy the files
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        os.system('cp -r ' + template_path + '/build-image ' + target_path)

        #replace the version number in the compile-src.sh
        os.system("sed -i '10s/versionNumber/" + version_commit + "/' " + target_path + "/build-image/compile-src.sh")

        subnet = utils.app_name_2_subnet(application)
        for i in range(1, num_node+1):
            ip = subnet + str(i+1)
            os.system("echo " + ip + " << " + target_path + "/build-image/regionservers")

        zookeeperIp = subnet + str(11)
        zookeeperIp = zookeeperIp.replace(".", "\.")
        os.system("sed -i 's/ZOOKEEPERIP/" + zookeeperIp + "/\' " + target_path + "/build-image/hbase-site.xml")

        #compile
        os.system('sh ' + target_path + "/build-image/compile-src.sh")

        #use the compiled file to build image.
        version.build_docker_image(True)

