
from cassandra.cluster import Cluster as PyCluster

class CQLTester():

    def __init__(self):
        self.table_number = 0
        self.keyspace_number = 0
        self.session = None
        self.KEYSPACE = 'cql_test_keyspace'
        self.KEYSPACE_PER_TEST = 'cql_test_keyspace_alt'
        self.USE_PREPARED_VALUES = True
        self.REUSE_PREPARED = True
        self.ROW_CACHE_SIZE_IN_MB = 0
        self.seqNumber = 0
        self.server = None
        self.nativePort = None
        self.nativeAddr = None
        self.clusters = {}
        self.sessions = {}
        self.isServerPrepared = True
        self.PROTOCOL_VERSIONS = []
        self.lastSchemaChangeResult = None
        self.keyspaces = []
        self.tables = []
        self.types = []
        self.functions = []
        self.aggregates = []
        self.usePrepared = self.USE_PREPARED_VALUES
        self.reusePrepared = self.REUSE_PREPARED
        self.createdTables = []

    def setUpClass(self, num_nodes, subnet):
        clusterList = []
        for i in range(2, (num_nodes + 2)):
            clusterList.append((subnet + str(i)))
        cluster = PyCluster(clusterList)
        self.session = cluster.connect(wait_for_all_pools=True)
        self.session.default_timeout = 60
        return self.session

    def beforeTest(self):
        self.schemaChange(("CREATE KEYSPACE IF NOT EXISTS %s WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}" % self.KEYSPACE))
        self.schemaChange(("CREATE KEYSPACE IF NOT EXISTS %s WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}" % self.KEYSPACE_PER_TEST))

    def keyspace(self):
        return self.KEYSPACE

    def currentTable(self):
        if (not self.tables):
            return None
        return self.tables[(len(self.tables) - 1)]

    def createKeyspace(self, query):
        currentKeyspace = self.createKeyspaceName()
        fullQuery = (query % currentKeyspace)
        print(fullQuery)
        self.schemaChange(fullQuery)
        return currentKeyspace

    def createKeyspaceName(self):
        currentKeyspace = ('keyspace_' + str(self.keyspace_number))
        self.keyspaces.append(currentKeyspace)
        return currentKeyspace

    def createTable(self, query, keyspace=None):
        if (keyspace == None):
            keyspace = self.KEYSPACE
        currentTable = self.createTableName()
        self.createdTables.append(((keyspace + '.') + currentTable))
        fullQuery = self.formatQuery(keyspace, query)
        self.session.execute(fullQuery)

    def createTableName(self):
        currentTable = ('table_' + str(self.table_number))
        self.table_number += 1
        self.tables.append(currentTable)
        return currentTable

    def schemaChange(self, query):
        self.execute(query)

    def formatQuery(self, query):
        return self.formatQuery(self.KEYSPACE, query)

    def formatQuery(self, keyspace, query):
        currentTable = self.currentTable()
        return (query if (currentTable == None) else (query % ((keyspace + '.') + currentTable)))

    def execute(self, query, values=[]):
        assert (query.count('?') == len(values))
        for value in values:
            if (type(value) == int):
                query = query.replace('?', str(value), 1)
            else:
                query = query.replace('?', (("'" + str(value)) + "'"), 1)
        if ('%s' in query):
            query = self.formatQuery(self.KEYSPACE, query)
        print(query)
        return self.session.execute(query)
