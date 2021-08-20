
import CQLTester

class SimpleQueryTest(CQLTester.CQLTester):

    def __init__(self):
        self.tester = CQLTester.CQLTester()

    def testDynamicCompactTables(self):
        self.tester.createTable('CREATE TABLE %s (k text, t int, v text, PRIMARY KEY (k, t));')
        self.tester.execute('INSERT INTO %s (k, t, v) values (?, ?, ?)', ['key', 1, 'v11'])
        self.tester.execute('INSERT INTO %s (k, t, v) values (?, ?, ?)', ['key', 2, 'v12'])
        self.tester.execute('INSERT INTO %s (k, t, v) values (?, ?, ?)', ['key', 3, 'v13'])
        self.tester.execute('INSERT INTO %s (k, t, v) values (?, ?, ?)', ['key', 4, 'v14'])
        self.tester.execute('INSERT INTO %s (k, t, v) values (?, ?, ?)', ['key', 5, 'v15'])

    def testTableWithoutClustering(self):
        self.tester.createTable('CREATE TABLE %s (k text PRIMARY KEY, v1 int, v2 text);')
        self.tester.execute('INSERT INTO %s (k, v1, v2) values (?, ?, ?)', ['first', 1, 'value1'])
        self.tester.execute('INSERT INTO %s (k, v1, v2) values (?, ?, ?)', ['second', 2, 'value2'])
        self.tester.execute('INSERT INTO %s (k, v1, v2) values (?, ?, ?)', ['third', 3, 'value3'])

    def testTableWithOneClustering(self):
        self.tester.createTable('CREATE TABLE %s (k text, t int, v1 text, v2 text, PRIMARY KEY (k, t));')
        self.tester.execute('INSERT INTO %s (k, t, v1, v2) values (?, ?, ?, ?)', ['key', 1, 'v11', 'v21'])
        self.tester.execute('INSERT INTO %s (k, t, v1, v2) values (?, ?, ?, ?)', ['key', 2, 'v12', 'v22'])
        self.tester.execute('INSERT INTO %s (k, t, v1, v2) values (?, ?, ?, ?)', ['key', 3, 'v13', 'v23'])
        self.tester.execute('INSERT INTO %s (k, t, v1, v2) values (?, ?, ?, ?)', ['key', 4, 'v14', 'v24'])
        self.tester.execute('INSERT INTO %s (k, t, v1, v2) values (?, ?, ?, ?)', ['key', 5, 'v15', 'v25'])

    def testTableWithReverseClusteringOrder(self):
        self.tester.createTable('CREATE TABLE %s (k text, t int, v1 text, v2 text, PRIMARY KEY (k, t)) WITH CLUSTERING ORDER BY (t DESC);')
        self.tester.execute('INSERT INTO %s (k, t, v1, v2) values (?, ?, ?, ?)', ['key', 1, 'v11', 'v21'])
        self.tester.execute('INSERT INTO %s (k, t, v1, v2) values (?, ?, ?, ?)', ['key', 2, 'v12', 'v22'])
        self.tester.execute('INSERT INTO %s (k, t, v1, v2) values (?, ?, ?, ?)', ['key', 3, 'v13', 'v23'])
        self.tester.execute('INSERT INTO %s (k, t, v1, v2) values (?, ?, ?, ?)', ['key', 4, 'v14', 'v24'])
        self.tester.execute('INSERT INTO %s (k, t, v1, v2) values (?, ?, ?, ?)', ['key', 5, 'v15', 'v25'])

    def testTableWithTwoClustering(self):
        self.tester.createTable('CREATE TABLE %s (k text, t1 text, t2 int, v text, PRIMARY KEY (k, t1, t2));')
        self.tester.execute('INSERT INTO %s (k, t1, t2, v) values (?, ?, ?, ?)', ['key', 'v1', 1, 'v1'])
        self.tester.execute('INSERT INTO %s (k, t1, t2, v) values (?, ?, ?, ?)', ['key', 'v1', 2, 'v2'])
        self.tester.execute('INSERT INTO %s (k, t1, t2, v) values (?, ?, ?, ?)', ['key', 'v2', 1, 'v3'])
        self.tester.execute('INSERT INTO %s (k, t1, t2, v) values (?, ?, ?, ?)', ['key', 'v2', 2, 'v4'])
        self.tester.execute('INSERT INTO %s (k, t1, t2, v) values (?, ?, ?, ?)', ['key', 'v2', 3, 'v5'])

    def testTableWithLargePartition(self):
        self.tester.createTable('CREATE TABLE %s (k text, t1 int, t2 int, v text, PRIMARY KEY (k, t1, t2));')
        t1 = 0
        while (t1 < 20):
            t2 = 0
            while (t2 < 10):
                self.tester.execute('INSERT INTO %s (k, t1, t2, v) values (?, ?, ?, ?)', ['key', t1, t2, ((('someSemiLargeTextForValue_' + t1) + '_') + t2)])
                t2 = (t2 + 1)
            t1 = (t1 + 1)
        expected = []
        t2 = 0
        while (t2 < 10):
            expected[t2] = self.tester.row('key', 15, t2)
            t2 = (t2 + 1)
        expectedReverse = []
        t2 = 9
        while (t2 >= 0):
            expectedReverse[(9 - t2)] = self.tester.row('key', 15, t2)
            t2 = (t2 + 1)

    def testRowDeletion(self):
        N = 4
        self.tester.createTable('CREATE TABLE %s (k text, t int, v1 text, v2 int, PRIMARY KEY (k, t));')
        t = 0
        while (t < N):
            self.tester.execute('INSERT INTO %s (k, t, v1, v2) values (?, ?, ?, ?)', ['key', t, ('v' + t), (t + 10)])
            t = (t + 1)
        i = 0
        while (i < (N / 2)):
            self.tester.execute('DELETE FROM %s WHERE k=? AND t=?', ['key', (i * 2)])
            i = (i + 1)
        expected = []
        i = 0
        while (i < (N / 2)):
            t = ((i * 2) + 1)
            expected[i] = self.tester.row('key', t, ('v' + t), (t + 10))
            i = (i + 1)

    def testRangeTombstones(self):
        N = 100
        self.tester.createTable('CREATE TABLE %s (k text, t1 int, t2 int, v text, PRIMARY KEY (k, t1, t2));')
        t1 = 0
        while (t1 < 3):
            t2 = 0
            while (t2 < N):
                self.tester.execute('INSERT INTO %s (k, t1, t2, v) values (?, ?, ?, ?)', ['key', t1, t2, ((('someSemiLargeTextForValue_' + t1) + '_') + t2)])
                t2 = (t2 + 1)
            t1 = (t1 + 1)
        self.tester.execute('DELETE FROM %s WHERE k=? AND t1=?', ['key', 1])
        expected = []
        t2 = 0
        while (t2 < N):
            expected[t2] = self.tester.row('key', 0, t2, ('someSemiLargeTextForValue_0_' + t2))
            expected[(N + t2)] = self.tester.row('key', 2, t2, ('someSemiLargeTextForValue_2_' + t2))
            t2 = (t2 + 1)

    def test2ndaryIndexes(self):
        self.tester.createTable('CREATE TABLE %s (k text, t int, v text, PRIMARY KEY (k, t));')
        self.tester.execute('CREATE INDEX ON %s(v)', [])
        self.tester.execute('INSERT INTO %s (k, t, v) values (?, ?, ?)', ['key1', 1, 'foo'])
        self.tester.execute('INSERT INTO %s (k, t, v) values (?, ?, ?)', ['key1', 2, 'bar'])
        self.tester.execute('INSERT INTO %s (k, t, v) values (?, ?, ?)', ['key2', 1, 'foo'])
        self.tester.execute('INSERT INTO %s (k, t, v) values (?, ?, ?)', ['key2', 2, 'foo'])
        self.tester.execute('INSERT INTO %s (k, t, v) values (?, ?, ?)', ['key2', 3, 'bar'])

    def testStaticColumns(self):
        self.tester.createTable('CREATE TABLE %s (k text, t int, s text static, v text, PRIMARY KEY (k, t));')
        self.tester.execute('INSERT INTO %s (k, t, v, s) values (?, ?, ?, ?)', ['key1', 1, 'foo1', 'st1'])
        self.tester.execute('INSERT INTO %s (k, t, v, s) values (?, ?, ?, ?)', ['key1', 2, 'foo2', 'st2'])
        self.tester.execute('INSERT INTO %s (k, t, v, s) values (?, ?, ?, ?)', ['key1', 3, 'foo3', 'st3'])
        self.tester.execute('INSERT INTO %s (k, t, v) values (?, ?, ?)', ['key1', 4, 'foo4'])
        self.tester.execute('INSERT INTO %s (k, t, v, s) values (?, ?, ?, ?)', ['key1', 2, 'foo2', 'st2-repeat'])
        self.tester.execute('INSERT INTO %s (k, t, v, s) values (?, ?, ?, ?)', ['key1', 5, 'foo5', 'st5'])
        self.tester.execute('INSERT INTO %s (k, t, v) values (?, ?, ?)', ['key1', 6, 'foo6'])

    def testDistinct(self):
        self.tester.createTable('CREATE TABLE %s (k text, t int, v text, PRIMARY KEY (k, t));')
        self.tester.execute('INSERT INTO %s (k, t, v) values (?, ?, ?)', ['key1', 1, 'foo1'])
        self.tester.execute('INSERT INTO %s (k, t, v) values (?, ?, ?)', ['key1', 2, 'foo2'])
        self.tester.execute('INSERT INTO %s (k, t, v) values (?, ?, ?)', ['key1', 3, 'foo3'])
        self.tester.execute('INSERT INTO %s (k, t, v) values (?, ?, ?)', ['key2', 4, 'foo4'])
        self.tester.execute('INSERT INTO %s (k, t, v) values (?, ?, ?)', ['key2', 5, 'foo5'])

    def collectionDeletionTest(self):
        self.tester.createTable('CREATE TABLE %s (k int PRIMARY KEY, s set<int>);')
        self.tester.execute('INSERT INTO %s (k, s) VALUES (?, ?)', [1, self.tester.set(1)])
        self.tester.execute('INSERT INTO %s (k, s) VALUES (?, ?)', [1, self.tester.set(2)])

    def limitWithMultigetTest(self):
        self.tester.createTable('CREATE TABLE %s (k int PRIMARY KEY, v int);')
        self.tester.execute('INSERT INTO %s (k, v) VALUES (?, ?)', [0, 0])
        self.tester.execute('INSERT INTO %s (k, v) VALUES (?, ?)', [1, 1])
        self.tester.execute('INSERT INTO %s (k, v) VALUES (?, ?)', [2, 2])
        self.tester.execute('INSERT INTO %s (k, v) VALUES (?, ?)', [3, 3])

    def staticDistinctTest(self):
        self.tester.createTable('CREATE TABLE %s ( k int, p int, s int static, PRIMARY KEY (k, p))')
        self.tester.execute('INSERT INTO %s (k, p) VALUES (?, ?)', [1, 1])
        self.tester.execute('INSERT INTO %s (k, p) VALUES (?, ?)', [1, 2])

    def test2ndaryIndexBug(self):
        self.tester.createTable('CREATE TABLE %s (k int, c1 int, c2 int, v int, PRIMARY KEY(k, c1, c2))')
        self.tester.execute('CREATE INDEX v_idx ON %s(v)', [])
        self.tester.execute('INSERT INTO %s (k, c1, c2, v) VALUES (?, ?, ?, ?)', [0, 0, 0, 0])
        self.tester.execute('INSERT INTO %s (k, c1, c2, v) VALUES (?, ?, ?, ?)', [0, 1, 0, 0])
        self.tester.execute('DELETE FROM %s WHERE k=? AND c1=?', [0, 1])

    def restrictionOnRegularColumnWithStaticColumnPresentTest(self):
        self.tester.createTable('CREATE TABLE %s (id int, id2 int, age int static, extra int, PRIMARY KEY(id, id2))')
        self.tester.execute('INSERT INTO %s (id, id2, age, extra) VALUES (?, ?, ?, ?)', [1, 1, 1, 1])
        self.tester.execute('INSERT INTO %s (id, id2, age, extra) VALUES (?, ?, ?, ?)', [2, 2, 2, 2])
        self.tester.execute('UPDATE %s SET age=? WHERE id=?', [3, 3])

    def testRowFilteringOnStaticColumn(self):
        self.tester.createTable('CREATE TABLE %s (id int, name text, age int static, PRIMARY KEY (id, name))')
        i = 0
        while (i < 5):
            self.tester.execute('INSERT INTO %s (id, name, age) VALUES (?, ?, ?)', [i, 'NameDoesNotMatter', i])
            i = (i + 1)

    def testSStableTimestampOrdering(self):
        self.tester.createTable('CREATE TABLE %s (k1 int, v1 int, v2 int, PRIMARY KEY (k1))')
        self.tester.execute('INSERT INTO %s(k1,v1,v2) VALUES(1,1,1)  USING TIMESTAMP 5', [])
        self.tester.execute('INSERT INTO %s(k1,v1,v2) VALUES(1,1,2)  USING TIMESTAMP 8', [])
        self.tester.execute('INSERT INTO %s(k1) VALUES(1)  USING TIMESTAMP 7', [])
        self.tester.execute('DELETE FROM %s USING TIMESTAMP 6 WHERE k1 = 1', [])
