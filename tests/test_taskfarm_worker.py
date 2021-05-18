import testtools
import taskfarm_worker
import requests_mock
from requests_mock.contrib import fixture

BASEURL = 'http://testlocation.org/api/'


class TestTFRuns(testtools.TestCase):
    @requests_mock.Mocker()
    def test_tfRuns(self, m):
        m.get(BASEURL + 'runs',
              json={'data': 'blub'})
        runs = taskfarm_worker.tfRuns('user', 'pw', url_base=BASEURL)
        self.assertEqual(runs, 'blub')


class BaseTest(testtools.TestCase):
    ntasks = 10
    uuid = 'A_UUID'

    def setUp(self):
        super(BaseTest, self).setUp()
        self.requests_mock = self.useFixture(fixture.Fixture())
        self.requests_mock.register_uri(
            'GET', BASEURL + 'token',
            json={'token': 'some_token'})


class TestTFCreateTF(BaseTest):
    def test_newTF_fail(self):
        with testtools.ExpectedException(RuntimeError):
            taskfarm_worker.TaskFarm('user', 'pw', url_base=BASEURL)

    def test_newTFnumTasks(self):
        self.requests_mock.register_uri(
            'POST', BASEURL + 'run',
            status_code=201,
            json={'uuid': self.uuid,
                  'numTasks': self.ntasks})

        tf = taskfarm_worker.TaskFarm('user', 'pw', url_base=BASEURL,
                                      numTasks=self.ntasks)
        self.assertEqual(tf.numTasks, self.ntasks)
        self.assertEqual(tf.uuid, self.uuid)

    def test_newTFUUID(self):
        self.requests_mock.register_uri(
            'GET', BASEURL + 'runs/' + self.uuid,
            json={'uuid': self.uuid,
                  'numTasks': self.ntasks})
        tf = taskfarm_worker.TaskFarm('user', 'pw', url_base=BASEURL,
                                      uuid=self.uuid)
        self.assertEqual(tf.numTasks, self.ntasks)
        self.assertEqual(tf.uuid, self.uuid)

class TestTF(BaseTest):
    pd = 40
    nd = 5
    nw = 2
    nc = 3
    
    def setUp(self):
        super(TestTF, self).setUp()
        # create a new run
        self.requests_mock.register_uri(
            'POST', BASEURL + 'run',
            status_code=201,
            json={'uuid': self.uuid,
                  'numTasks': self.ntasks})
        self.tf = taskfarm_worker.TaskFarm('user', 'pw', url_base=BASEURL,
                                           numTasks=self.ntasks)

    def test_info(self):
        info = {
            'percentDone': self.pd,
            'numDone': self.nd,
            'numWaiting': self.nw,
            'numComputing': self.nc}
        self.requests_mock.register_uri(
            'GET', BASEURL + 'runs/' + self.uuid + '?info=',
            json=info)
        res = self.tf.info('')
        for k in info:
            self.assertEqual(res[k], info[k])
        
    def test_percentageDone(self):
        self.requests_mock.register_uri(
            'GET', BASEURL + 'runs/' + self.uuid + '?info=percentDone',
            json={'percentDone': self.pd})
        self.assertEqual(self.tf.percentDone, self.pd)

    def test_numDone(self):
        self.requests_mock.register_uri(
            'GET', BASEURL + 'runs/' + self.uuid + '?info=numDone',
            json={'numDone': self.nd})
        self.assertEqual(self.tf.numDone, self.nd)

    def test_numWaiting(self):
        self.requests_mock.register_uri(
            'GET', BASEURL + 'runs/' + self.uuid + '?info=numWaiting',
            json={'numWaiting': self.nw})
        self.assertEqual(self.tf.numWaiting, self.nw)

    def test_numComputing(self):
        self.requests_mock.register_uri(
            'GET', BASEURL + 'runs/' + self.uuid + '?info=numComputing',
            json={'numComputing': self.nc})
        self.assertEqual(self.tf.numComputing, self.nc)
