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


class TestTFCreateTF(testtools.TestCase):
    def setUp(self):
        super(TestTFCreateTF, self).setUp()
        self.requests_mock = self.useFixture(fixture.Fixture())
        self.requests_mock.register_uri(
            'GET', BASEURL + 'token',
            json={'token': 'some_token'})

    def test_newTF_fail(self):
        with testtools.ExpectedException(RuntimeError):
            taskfarm_worker.TaskFarm('user', 'pw', url_base=BASEURL)

    def test_newTFnumTasks(self):
        ntasks = 10
        uuid = 'A_UUID'
        self.requests_mock.register_uri(
            'POST', BASEURL + 'run',
            status_code=201,
            json={'uuid': uuid,
                  'numTasks': ntasks})

        tf = taskfarm_worker.TaskFarm('user', 'pw', url_base=BASEURL,
                                      numTasks=ntasks)
        self.assertEqual(tf.numTasks, ntasks)
        self.assertEqual(tf.uuid, uuid)

    def test_newTFUUID(self):
        ntasks = 10
        uuid = 'A_UUID'
        self.requests_mock.register_uri(
            'GET', BASEURL + 'runs/' + uuid,
            json={'uuid': uuid,
                  'numTasks': ntasks})
        tf = taskfarm_worker.TaskFarm('user', 'pw', url_base=BASEURL,
                                      uuid=uuid)
        self.assertEqual(tf.numTasks, ntasks)
        self.assertEqual(tf.uuid, uuid)
