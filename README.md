**DUPTester reproduces results in our paper's section 6.1 Table 5.**

# DUPTester

- ./src: The scripts to run stressing or unit upgrade test for all systems to reproduce bugs.
- ./systems: Files required to build docker images of different versions of each systems.
- ./tests: Directory used to store the data and logs generated by tests.
- ./test-migrator-based-python: Script to translate Cassandra unit tests from Java to Python, and generate upgrade tests for each unit test.


# Evaluation Requirements:
1. Intel(R) Xeon(R) CPU E5-2630 v3 @ 2.40GHz
2. Time distribution: install dependencies and download required git repos - ~30 min, run experiements - ~2 hours.
3. Java = 1.8
4. Python 3.6+
5. Python3-pip

Note:If there are other versions of java in the original system, install openjdk-8-jdk and use java8 by following the steps blow:
```
sudo apt-get install openjdk-8-jdk
```
List all java versions and switch to java8:
```
update-java-alternatives --list
sudo update-java-alternatives --set /path/to/java/version
```
where /path/to/java/version is one of those listed by the previous command (e.g. /usr/lib/jvm/java-7-openjdk-amd64).

# Reproduce results in paper:

  ### Set up DUPTester:
  * Run script to install dependencies, and checkout required applications.
    - Note that the dependency installation commands work on ubuntu. You might
      want to change the commands if you are using other OS.
  * The application includes: Cassandra, Hbase, Hive, Kafka, and Zookeeper.
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

  ### Failure Reproduce
  * Run script to reproduce the failure we detected by using DUPTester.
  * It 
    - 1) uses compiled target system (e.g., cassandra.tar.gz),
    - 2) construct docker images,
    - 3) and set up a docker cluster to execute the upgrade test.
  * Compilation takes time and sometimes requires special dependencies, so we provide
    compiled tar.gz files.
  * After the build image is completed, it takes about 5 minutes to execute a test.
  ```
  cd DUPTester/src
  python3 reproduce_upgrade_bugs.py
  ```

  ### Unit test migration
  * It is a tool to migrate cassandra unit test from java to python.
  * The unit test required to reproduce failure is already translated and run in Failure Reproduce section.
  * If you want to run the translator for Cassandra:

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

   * The translated tests are saved in ./test-migrator-based-python/migrate_result
   * The generated upgrade tests are saved in ./src/cass/generated_test

# Special Attention
If you cannot reproduce our results using this repo, please contact us and we will provide a virtual machine image.
