import os,time

curr_dir = os.path.dirname(os.path.abspath(__file__))
mig_dir = os.path.join(curr_dir, "..", "..", "test-migrator-based-python")
base_file = os.path.join(mig_dir, "base_file.py")


os.system("cp " + base_file + "16292 " + base_file)
os.system("rm -rf " + curr_dir + "/generated_test")
os.system("mkdir " + curr_dir + "/generated_test")
os.system("python3 " + mig_dir + "/multiple_tests_generator.py")
os.system("cp " + mig_dir + "/generated_files/unitTest_cass_PstmtPersistenceTest_testCachedPreparedStatements_upgrade_test.py " + curr_dir+"/generated_test")
os.system("python3 " + curr_dir + "/generated_test/"
                  + "unitTest_cass_PstmtPersistenceTest_testCachedPreparedStatements_upgrade_test.py")

