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

def reproCases(loop, count=0):
    i = 20
    if loop == -1:
        for cases in df.index:
            print(str(cases) + ". " + df.iloc[cases,0])
        case_number = int(input("Select the case number(eg. 5):"))
    else:
        case_number = loop
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
        zk_version.build_docker_image(True)
        old_version = hbase.hbase_upgrade_path.HbaseVersion(application, from_version)
        new_version = hbase.hbase_upgrade_path.HbaseVersion(application, target_version)
    elif abbr == "hive":
        hdfs_version = upgrade_path.Version("hdfs", "hdfs_for_hive")
        hdfs_version.build_docker_image(True)
        hdfs_version = upgrade_path.Version("hdfs", "release-2.9.0")
        hdfs_version.build_docker_image(True)
        old_version = hive.hive_upgrade_path.HiveVersion(application, from_version)
        new_version = hive.hive_upgrade_path.HiveVersion(application, target_version)
    else:
        old_version = upgrade_path.Version(application, from_version)
        new_version = upgrade_path.Version(application, target_version)

    old_version.build_docker_image(True)
    new_version.build_docker_image(True)

    target_dir = curr_dir + abbr

    if ticket == "CASSANDRA-16267":
        os.system("python3 " + target_dir + "/" + "cass_16267_upgrade_test.py")
    elif ticket == "CASSANDRA-16264":
        os.system("python3 " + target_dir + "/" + "cass_16264_upgrade_test.py")
    elif ticket == "CASSANDRA-16266":
        os.system("python3 " + target_dir + "/" + "cass_16266_upgrade_test.py")
        #print("16266")
    elif ticket == "CASSANDRA-16258":
        os.system("python3 " + target_dir + "/" + "cass_16258_upgrade_test.py")
    elif ticket == "CASSANDRA-16269":
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

    if reproduce_succ:
        print("*********************************Reproduce Result**********************************")
        print("[Result] : " + ticket + " Failure Reproduced Successfully!")
    else:
        if count == 5:
            print("*********************************Reproduce Result**********************************")
            print("[Result] : "+ ticket +" Failure Reproduced Failed")
        else:
            count += 1
            reproCases(case_number, count)
            return

    print("If you want to check the result, please run: sudo grep \"" + bug_type + "\" -nr + test_log_dir >> check_result.log ")
    print("************************************************************************************ >> check_result.log")

    return reproduce_succ, ticket

if __name__ == '__main__':

    while True:
        #option = input("A. Reproduce all failures. \nB. Select the case number you want to reproduce. \nC. Exit\n")
        option = 'A'
        if option not in ['A', 'B', 'C']:
            print("Invaild input")
            continue

        if option == 'C':
            break
        elif option == 'A':
            failed_case = []
            for i in range(0, 20):
                repro_result, ticket = reproCases(i)
                if repro_result == False:
                    failed_case.append(ticket)
            if len(failed_case):
                print("[Result] : Reproduced Failed Cases: ")
                for case in failed_case:
                    print("         " + case)
            else:
                print("[Result] : All cases reproduced successfully!!")
            break
        elif option == 'B':
            reproCases(-1)
