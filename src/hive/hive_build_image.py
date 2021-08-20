import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import hive_upgrade_path
import utils

class HiveBuildImage():

    def build_image(self, abbr, application, version_commit, version_number, num_node, force):

        version = hive_upgrade_path.HbaseVersion(application, version_number)
        curr_dir = os.path.dirname(os.path.abspath(__file__))

        # the target path and the template path which the files should copy from
        target_path = curr_dir + '/../../systems/' + abbr + '/' + version_number
        template_path = curr_dir + '/../../systems/' + abbr + '/template'


        #create the directory and copy the files
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        os.system('cp -r ' + template_path + '/build-image ' + target_path)

        #replace the version number in the compile-src.sh
        os.system("sed -i '8s/versionNumber/" + version_commit + "/' " + target_path + "/build-image/compile-src.sh")

        #compile
        os.system('sh ' + target_path + "/build-image/compile-src.sh")

        #use the compiled file to build image.
        version.build_docker_image(True)

