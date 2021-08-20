
import CQLTester

class PstmtPersistenceTest(CQLTester.CQLTester):

    def __init__(self):
        self.tester = CQLTester.CQLTester()

    def testCachedPreparedStatements(self):
        self.tester.execute("CREATE KEYSPACE IF NOT EXISTS foo WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}", [])
        self.tester.execute('CREATE TABLE foo.bar (key text PRIMARY KEY, val int)', [])
        self.tester.createTable('CREATE TABLE %s (pk int PRIMARY KEY, val text)')
        self.tester.execute('DROP KEYSPACE foo', [])

    def testPstmtInvalidation(self):
        self.tester.createTable('CREATE TABLE %s (key int primary key, val int)')
