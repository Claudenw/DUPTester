# DUPTester

- ./src: The scripts to run stressing or unit upgrade test for all systems to reproduce bugs.
- ./systems: Files required to build images of different versions of each systems.
- ./dataVerify: Script and cases info to verify data we write in paper.
- ./tests: Directory used to store the data and logs  generated by tests.
- ./test-migrator-based-python: Script to mirgrate Cassandra unit tests from Java to Python, and generate upgrade tests for each unit test.


# Evaluation Requirements:
1. Intel(R) Xeon(R) CPU E5-2630 v3 @ 2.40GHz
2. Time distribution: install dependencies and download required git repos - ~20 min, run experiements - ~4 hours.
3. Java >= 1.8 (OpenJDK and Oracle JVMS have been tested)
4. Python 3.6+
5. Python3-pip

# Getting started:
  ### Set up DUPTester:
  * Run script to install dependencies, and checkout required applications.
  * The application includes: Cassandra, Hbase, Hive, Kafka, Zookeeper, and Hdfs.
  * The script will clone the source code of these applications from github.
  * The applications are stored in ./applications
  ```
  bash DUPTester-setup.sh
  ```
  * In order to use docker, you need to add your user to docker group.
  ```
  sudo gpasswd -a $USER docker
  newgrp docker
  ```
  
  ### Data Verification
  * Run script to verify the data we metioned in paper and obtained from our study.
  * And follow the steps to select data you want to verify.
  ```
  cd DUPTester/dataVerify
  python3 dataVerfication.py
  ```
  
  ### Failure Reproduce
  * Run script to reproduce the failure we detected by using DUPTester.
  * It use docker as the container to run each application, so we need to build image for applications and versions required.
  * Compilation is required before build image. 
  * Compilation generally takes five minutes or more, while Hbase may take ten minutes or more.
  * After the build image is completed, it takes about 5 minutes to execute the test, and there will be some differences in the time required for each test.
  ```
  cd DUPTester/src
  python3 reproduce_upgrade_bugs.py
  ```
  
  ### Unit test migration
  * The unit test required to reproduce failure is already migrated and run in Failure Reproduce section.
  * Run script to migrate unit test for Cassandra.
  * It is a tool to migrate cassandra unit test from java to python.
  * It require some maunally works.
  
	1. Copy the unit test java file to DUPTester/test-migrator-based-python/java_files.
	   Cassandra unit test is located at: applications/cassandra/test/unit/org/apache/cassandra/
	2. Set upgrade test configuration in DUPTester/test-migrator-based-python/base_file.py
	   The Configuration includes: old and new version number, number of nodes, number of seeds, and if rolling upgrade required.
	```
	old_version = cass_upgrade_path.CassVersion("cassandra", old_version_number)
	new_version = cass_upgrade_path.CassVersion("cassandra", new_version_number)
	config = Config(number_of_node, number_of_seed)
	application_start_interval = 120
	upgrade_edge = cass_upgrade_path.CassUpgradeEdge(old_version, new_version)

	test = testClassName(upgrade_edge, config, application_start_interval,
                     "unittest", testName, str(testId))
	#if rolling upgrade required
	test.test_rolling_upgrade()
	#if rolling upgrade not required
	test.test_upgrade()
	```
   * Run the script
  ```
  cd DUPTester/test-migrator-based-python
  python3 multiple_tests_generator.py
  ```

   * The migrated tests are saved in submit/test-migrator-based-python/migrate_result
   * The generated upgrade tests are saved in submit/src/cass/generated_test

## If you cannot reproduce our results using this repo, please contact us and we will provide a virtual machine image.
