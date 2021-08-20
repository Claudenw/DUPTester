import utils
import argparse
import os
import subprocess
import hbase.hbase_build_image
import cass.cass_build_image
import hive.hive_build_image


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Generate the docker images of the application to perform the upgrade test.',
        epilog='Example usage: python test_build_image.py cassandra cassandra-3.10 -c 3cf415279c171fe20802ad90f181eed7da04c58d')

    parser.add_argument("application", help="name of the application")
    parser.add_argument("-c", "--commit", default=None, help="the git commit of the version")
    parser.add_argument("version_number", help="the version number of the application ")
    parser.add_argument("-f", "--force", action="store_true", default=False, help="force to use old jdk to compile")
    parser.add_argument("-n", "--numberOfNode", default=3, help="the number of nodes")

    args = parser.parse_args()

    application = args.application
    abbr = utils.app_name_2_abbr(application)

    # if git commit is not provided, then use the version number
    if args.commit == None:
        version_commit = args.version_number
    # otherwise, replace the version number in the compile-src.sh by the commit number
    else:
        version_commit = args.commit

    # get other arguments
    version_number = args.version_number
    num_node = args.numberOfNode
    force = args.force

    curr_dir = os.path.dirname(os.path.abspath(__file__))

    if abbr == "cass":
        imageBuilder = cass.cass_build_image.CassBuildImage()
    elif abbr == "hbase":
        file_path = curr_dir + "../systems/zk/branch-3.6/build-image"
        os.system("bash " + file_path + "compile-src.sh")
        os.system("docker build -t zk-branch-3.6 " + file_path + "./")
        imageBuilder = hbase.hbase_build_image.HbaseBuildImage()
    elif abbr == "hive":
        file_path = curr_dir + "../systems/hdfs/hdfs_for_hive/build-image-single-node/"
        os.system("bash " + file_path + "compile-src.sh")
        os.system("docker build -t hdfs_for_hive" + file_path + "./")
        cmd = 'CMD ["/usr/bin/supervisord"]'
        os.system("echo " + cmd + " >> " + file_path + "Dockerfile")
        os.system("docker build -t image_hdfs_release-2.9.0 " + file_path + "./")

        imageBuilder = hbase.hive_build_image.HiveBuildImage()

    imageBuilder.build_image(abbr, application, version_commit, version_number, num_node, force)

