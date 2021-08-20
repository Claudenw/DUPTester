
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'test-migrator-based-python', 'migrate_result'))
import cass_upgrade_path
from cass_config import cassConfig as Config
import utils, upgrade_test_base, upgrade_path
from cassandra.cluster import Cluster as PyCluster
createdTables = []
import CQLTester
import PstmtPersistenceTest
testId = 1
testName = 'PstmtPersistenceTest_testPstmtInvalidation'

class casstestPstmtInvalidationUpgradeTest(upgrade_test_base.UpgradeTestBase):

    def test_new_version(self, test_node_id):
        num_nodes = self.config.num_nodes
        subnet = ((utils.app_name_2_subnet(old_version.application.name) + str(testId)) + '.')
        test = PstmtPersistenceTest.PstmtPersistenceTest()
        test.tester.setUpClass(num_nodes, subnet)
        test.tester.beforeTest()
        for table in createdTables:
            try:
                res = test.tester.execute(('SELECT * FROM ' + table))
                rowNum = 0
                for row in res:
                    rowNum = (rowNum + 1)
                    print(row)
                print((('There are totally ' + str(rowNum)) + ' rows.'))
            except Exception as e:
                print(e)
                pass

    def test_old_version(self):
        num_nodes = self.config.num_nodes
        subnet = ((utils.app_name_2_subnet(old_version.application.name) + str(testId)) + '.')
        test = PstmtPersistenceTest.PstmtPersistenceTest()
        test.tester.setUpClass(num_nodes, subnet)
        test.tester.beforeTest()
        test.testPstmtInvalidation()
        createdTables.extend(test.tester.createdTables)
if (__name__ == '__main__'):
    old_version = cass_upgrade_path.CassVersion('cassandra', 'cassandra-3.11.4')
    new_version = cass_upgrade_path.CassVersion('cassandra', 'cassandra-3.11.9')
    config = Config(3, 1)
    application_start_interval = 120
    upgrade_edge = cass_upgrade_path.CassUpgradeEdge(old_version, new_version)
    test = casstestPstmtInvalidationUpgradeTest(upgrade_edge, config, application_start_interval, 'unittest', testName, str(testId))
    test.test_upgrade()
