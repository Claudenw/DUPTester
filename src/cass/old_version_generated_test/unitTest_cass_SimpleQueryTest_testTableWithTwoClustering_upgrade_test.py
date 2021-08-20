import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import cass_upgrade_path
from cass_config import cassConfig as Config
import utils, upgrade_test_base, upgrade_path
from cassandra.cluster import Cluster as PyCluster

class casstestTableWithTwoClusteringUpgradeTest(upgrade_test_base.UpgradeTestBase):

    def getSession(self):
        clusterList = []
        for i in range(2, self.config.num_nodes + 2):
            clusterList.append(utils.app_name_2_subnet(old_version.application.name) + "26." + str(i))
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

        session.execute("CREATE TABLE testTable (k text, t1 text, t2 int, v text, PRIMARY KEY (k, t1, t2));")
        session.execute("INSERT INTO testTable (k, t1, t2, v) values ({}, {}, {}, {})".format("'" + "key" + "'", "'" + "v1" + "'", 1, "'" + "v1" + "'"))
        session.execute("INSERT INTO testTable (k, t1, t2, v) values ({}, {}, {}, {})".format("'" + "key" + "'", "'" + "v1" + "'", 2, "'" + "v2" + "'"))
        session.execute("INSERT INTO testTable (k, t1, t2, v) values ({}, {}, {}, {})".format("'" + "key" + "'", "'" + "v2" + "'", 1, "'" + "v3" + "'"))
        session.execute("INSERT INTO testTable (k, t1, t2, v) values ({}, {}, {}, {})".format("'" + "key" + "'", "'" + "v2" + "'", 2, "'" + "v4" + "'"))
        session.execute("INSERT INTO testTable (k, t1, t2, v) values ({}, {}, {}, {})".format("'" + "key" + "'", "'" + "v2" + "'", 3, "'" + "v5" + "'"))
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

    old_version = cass_upgrade_path.CassVersion("cassandra", "cassandra-2.0.0")
    new_version = cass_upgrade_path.CassVersion("cassandra", "cassandra-2.1.0")
    config = Config(10, 1)
    application_start_interval = 150
    upgrade_edge = cass_upgrade_path.CassUpgradeEdge(old_version, new_version)

    test = casstestTableWithTwoClusteringUpgradeTest(upgrade_edge, config, application_start_interval, 
           "unittest", "SimpleQueryTest_testTableWithTwoClustering", "26" )
    #test.test_rolling_upgrade()

    test.test_upgrade()

