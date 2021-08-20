import sys, os
import subprocess
import cass_upgrade_path

class CassBuildImage():

    def build_image(self, abbr, application, version_commit, version_number, num_node, force):

        version = cass_upgrade_path.CassVersion(application, version_number)
        curr_dir = os.path.dirname(os.path.abspath(__file__))

        # the target path and the template path which the files should copy from
        target_path = curr_dir + '/../../systems/' + abbr + '/' + version_number
        template_path = curr_dir + '/../../systems/' + abbr + '/template'


        #create the directory and copy the files
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        os.system('cp -r ' + template_path + '/build-image ' + target_path)


        # if force==True, old jdk required, compile in the docker container with the old jdk
        if force==True:
            test_dir = target_path + '/compile-src'
            os.system('cp -r ' + template_path + "/compile-src " + test_dir)
            #replace the version number in the compile-src.sh
            os.system("sed -i '13s/versionNumber/" + version_commit + "/' " + test_dir + "/prepare-src.sh")
            os.system('sh ' + target_path + '/compile-src/prepare-src.sh')
            before ='<artifact:remoteRepository id=\\\"central\\\"   url=\\\"\${artifact\.remoteRepository\.central}\\\"\/>'
            after = '<artifact:remoteRepository id=\\\"central\\\"   url=\\\"https:\/\/repo1\.maven\.org\/maven2\/\\\"\/>'
            command = 'sed -i \'s/' + before + '/' + after +'/\' ' + test_dir + "/src/cassandra/build.xml"
            os.system(command)
            if version_number == "cassandra-2.0.0":
                command = 'sed -i \'77s/http/https/\' ' + test_dir + "/src/cassandra/build.xml"
                os.system(command)

            #build the image with the old jdk
            os.system('sh ' + target_path + '/compile-src/build-docker-image.sh')
            test_dir = target_path + '/compile-src'
            yml_file = test_dir + '/docker-compose.yml'
            p = subprocess.Popen(['docker-compose', '-f', yml_file, 'up', '-d'], cwd=test_dir)
            p.wait()
            container_name = "compile-cass"

            #compile in the container
            p = subprocess.Popen(['docker', 'exec', container_name,
                                  'bash', '/compile-src/compile-src.sh'], cwd = test_dir)
            p.wait()

            #teardown the compile container
            p = subprocess.Popen(['docker-compose', '-f', yml_file, 'down'], cwd=test_dir)
            p.wait()

            #copy the compiled file to build-image directory
            os.system('cp ' + test_dir + '/src/cassandra.tar.gz ' + target_path + '/build-image/')

        else:
            #replace the version number in the compile-src.sh
            os.system("sed -i '8s/versionNumber/" + version_commit + "/' " + target_path + "/build-image/compile-src.sh")

            #compile
            os.system('sh ' + target_path + "/build-image/compile-src.sh")

        #use the compiled file to build image.
        version.build_docker_image(True)

