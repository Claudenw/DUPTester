import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils
import pandas as pd
import upgrade_path
import cass.cass_upgrade_path
import hbase.hbase_upgrade_path
import hive.hive_upgrade_path

dataFrame = pd.read_csv('cases.csv')
df = dataFrame.fillna('N/A')
df.set_index("Case")
curr_dir = os.path.dirname(os.path.abspath(__file__)) + "/"

def reproCases():
    i = 0
    for cases in df.index:
        print(str(cases) + ". " + df.iloc[cases,0])
        i=i+1

    case_number = int(input("Select the case number(eg. 5):"))
    while case_number<0 or case_number>i:
        print("Invaild input")
        case_number = int(input("Select the case number:"))

    ticket = df.iloc[case_number, 0]
    application = df.iloc[case_number, 1]
    abbr = utils.app_name_2_abbr(application)
    from_version = df.iloc[case_number, 2]
    target_version = df.iloc[case_number, 3]
    isRollingUpgrade = df.iloc[case_number, 4]
    num_nodes = df.iloc[case_number, 5]
    num_seeds = df.iloc[case_number, 6]
    bug_type = df.iloc[case_number, 7]

    if abbr == "cass":
        print(ticket)
        print(from_version)
        print(target_version)

        old_version = cass.cass_upgrade_path.CassVersion(application, from_version)
        new_version = cass.cass_upgrade_path.CassVersion(application, target_version)
    elif abbr == "hbase":
        zk_version = upgrade_path.Version("zookeeper", "branch-3.6")
        zk_version.build_docker_image(False)
        old_version = hbase.hbase_upgrade_path.HbaseVersion(application, from_version)
        new_version = hbase.hbase_upgrade_path.HbaseVersion(application, target_version)
    elif abbr == "hive":
        hdfs_version = upgrade_path.Version("hdfs", "hdfs_for_hive")
        hdfs_version.build_docker_image(False)
        hdfs_version = upgrade_path.Version("hdfs", "release-2.9.0")
        hdfs_version.build_docker_image(False)
        old_version = hive.hive_upgrade_path.HiveVersion(application, from_version)
        new_version = hive.hive_upgrade_path.HiveVersion(application, target_version)
    else:
        old_version = upgrade_path.Version(application, from_version)
        new_version = upgrade_path.Version(application, target_version)

    old_version.build_docker_image(False)
    new_version.build_docker_image(False)

    target_dir = curr_dir + abbr

    if ticket == "CASSANDRA-16267":
        os.system("python3 " + target_dir + "/" + "cass_16267_upgrade_test.py")
    elif ticket == "CASSANDRA-16264":
        os.system("python3 " + target_dir + "/" + "cass_16264_upgrade_test.py")
    if ticket == "CASSANDRA-16269":
        os.system("python3 " + target_dir + "/" + "cass_16269_upgrade_test.py")
    elif ticket == "CASSANDRA-16301":
        os.system("python3 " + target_dir + "/" + "cass_16301_upgrade_test.py")
    elif ticket == "CASSANDRA-16292":
        os.system("python3 " + target_dir + "/" + "cass_16292_upgrade_test.py")
    elif ticket == "CASSANDRA-16257":
        os.system("python3 " + target_dir + "/" + "cass_16257_upgrade_test.py")
    elif ticket == "HBASE-24556":
        os.system("python3 " + target_dir + "/" + "hbase_24556_upgrade_test.py")
    elif ticket == "HBASE-24430":
        os.system("python3 " + target_dir + "/" + "hbase_24430_upgrade_test.py")
    elif ticket == "HIVE-24493":
        os.system("python3 " + target_dir + "/" + "hive_24493_upgrade_test.py")
    elif ticket == "KAFKA-10041":
        os.system("python3 " + target_dir + "/" + "kafka_10041_upgrade_test.py")
    else:
        command = "python3 " + target_dir + "/" + abbr + "_stressing_upgrade_test.py " + from_version + " " + target_version \
                  + " -n " + str(num_nodes) + " -s " + str(num_seeds)

        if isRollingUpgrade == 1:
            command += " -r"
        print(command)
        os.system(command)

    reproduce_succ = False
    reproduce_result = os.path.join(curr_dir, "reproduce_result", "result")
    reproduce_log = os.path.join(curr_dir, "reproduce_result", "log")
    fp = open(reproduce_result, "r")
    f = open(reproduce_log, "r")
    if bug_type in fp.read():
        reproduce_succ = True
    if bug_type in f.read():
        reproduce_succ = True

    print("*********************************Reproduce Result**********************************")
    if reproduce_succ:
        print("[Result] : Failure Reproduced Successfully!")
    else:
        print("[Result] : Failure Reproduced Failed")

    print("     If you want to check the result, please run: sudo grep \"" + bug_type + "\" -nr + test_log_dir  ")
    print("************************************************************************************")

if __name__ == '__main__':

    while True:
        option = input("A. Select the case number you want to reproduce. \nB. Manually provide the application and "
                       "version information. \nC. Exit\n")

        if option not in ['A', 'B', 'C']:
            print("Invaild input")
            continue

        if option == 'C':
            break
        elif option == 'A':
            reproCases()
        elif option == 'B':
            print("TBD")
