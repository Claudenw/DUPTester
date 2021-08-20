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

    if abbr == "cass":
        old_version = cass.cass_upgrade_path.CassVersion(application, from_version)
        new_version = cass.cass_upgrade_path.CassVersion(application, target_version)
    elif abbr == "hbase":
        hdfs_version = upgrade_path.Version("hdfs", "hdfs_for_hive")
        hdfs_version.build_docker_image(False)
        old_version = hbase.hbase_upgrade_path.HbaseVersion(application, from_version)
        new_version = hbase.hbase_upgrade_path.HbaseVersion(application, target_version)
    elif abbr == "hive":
        zk_version = upgrade_path.Version("zookeeper", "branch-3.6")
        zk_version.build_docker_image(False)
        old_version = hive.hive_upgrade_path.HiveVersion(application, from_version)
        new_version = hive.hive_upgrade_path.HiveVersion(application, target_version)
    else:
        old_version = upgrade_path.Version(application, from_version)
        new_version = upgrade_path.Version(application, target_version)

    old_version.build_docker_image(False)
    new_version.build_docker_image(False)

    target_dir = curr_dir + abbr

    if ticket == "CASSANDRA-16267":
        os.system("python " + target_dir + "/" + "cass_16267_upgrade_test.py")
    elif ticket == "CASSANDRA-16301":
        os.system("python " + target_dir + "/" + "cass_16301_upgrade_test.py")
    elif ticket == "CASSANDRA-16292":
        os.system("python " + target_dir + "/generated_test/"
                  + "unitTest_cass_PstmtPersistenceTest_testCachedPreparedStatements_upgrade_test.py")
    elif ticket == "CASSANDRA-16257":
        os.system("python " + target_dir + "/generated_test/"
                  + "unitTest_cass_SimpleQueryTest_testTableWithTwoClustering_upgrade_test.py")
    elif ticket == "HBASE-24556":
        os.system("python " + target_dir + "/" + "hbase_24556_upgrade_test.py")
    elif ticket == "HBASE-24430":
        os.system("python " + target_dir + "/" + "hbase_24430_upgrade_test.py")
    elif ticket == "KAFKA-10041":
        os.system("python " + target_dir + "/" + "kafka_10041_upgrade_test.py")
    else:
        command = "python " + target_dir + "/" + abbr + "_stressing_upgrade_test.py " + from_version + " " + target_version \
                  + " -n " + str(num_nodes) + " -s " + str(num_seeds)

        if isRollingUpgrade == 1:
            command += " -r"
        print(command)
        os.system(command)

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
