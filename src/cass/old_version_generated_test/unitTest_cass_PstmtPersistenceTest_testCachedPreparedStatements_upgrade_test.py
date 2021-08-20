import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import cass_upgrade_path
from cass_config import cassConfig as Config
import utils, upgrade_test_base, upgrade_path
from cassandra.cluster import Cluster as PyCluster

class casstestCachedPreparedStatementsUpgradeTest(upgrade_test_base.UpgradeTestBase):

    def getSession(self):
        clusterList = []
        for i in range(2, self.config.num_nodes + 2):
            clusterList.append(utils.app_name_2_subnet(old_version.application.name) + "20." + str(i))
        cluster = PyCluster(clusterList)
        session = cluster.connect(wait_for_all_pools=True)
        session.default_timeout = 60
        #session.consistency_level = 'ONE'
        return session


    def createKeySpace(self):
        session = self.getSession()
        session.execute("CREATE KEYSPACE ks WITH replication = "
                        "{ 'class':'SimpleStrategy', 'replication_factor':1} "
                        "AND DURABLE_WRITES = true")
        session.execute("USE ks")
        return session

    def test_old_version(self):
        session = self.createKeySpace()
        print('Start Test')

        session.execute("CREATE KEYSPACE IF NOT EXISTS foo WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}")
        session.execute("CREATE TABLE foo.bar (key text PRIMARY KEY, val int)")
        session.execute("CREATE TABLE testTable (pk int PRIMARY KEY, val text)")
        session.execute("DROP KEYSPACE foo")
        try:
            res = session.execute("SELECT * FROM testTable")
            rowNum = 0
            for row in res:
                rowNum = rowNum + 1
                print(row)
            print('There are totally ' + str(rowNum) + ' rows.')
        except Exception as e:
            print(e)
            pass

    def test_new_version(self, test_node_id):
        session = self.getSession() 
        session.execute("USE ks")
        print ('------------- ' + str(test_node_id) + ' starts testing. ------------')
        try:
            res = session.execute("SELECT * FROM testTable")
            rowNum = 0
            for row in res:
                rowNum = rowNum + 1
                print(row)
            print('There are totally ' + str(rowNum) + ' rows.')
        except Exception as e:
            print(e)
            pass
	print ( '************' + str(test_node_id) + ' is tested.**********')

        #session.execute("DROP KEYSPACE ks")

if __name__ == '__main__':

    old_version = cass_upgrade_path.CassVersion("cassandra", "cassandra-3.0")
    new_version = cass_upgrade_path.CassVersion("cassandra", "cassandra-3.2")
    config = Config(3, 1)
    application_start_interval = 150
    upgrade_edge = cass_upgrade_path.CassUpgradeEdge(old_version, new_version)

    test = casstestCachedPreparedStatementsUpgradeTest(upgrade_edge, config, application_start_interval, 
           "unittest", "PstmtPersistenceTest_testCachedPreparedStatements", "20" )
    #test.test_rolling_upgrade()

    test.test_upgrade()

