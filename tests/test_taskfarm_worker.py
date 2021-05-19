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
    ntasks = 5
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

    tpd = 34
    status = 'computing'

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

    def test_get_taskInfo_fail(self):
        with testtools.ExpectedException(RuntimeError):
            self.tf.getTaskInfo(-1, 'blub')
        with testtools.ExpectedException(RuntimeError):
            self.tf.getTaskInfo(self.ntasks, 'blub')

    def test_get_taskInfo_percent(self):
        self.requests_mock.register_uri(
            'GET',
            BASEURL + 'runs/' + self.uuid + '/tasks/0'
            '?info=percentCompleted',
            json={'percentCompleted': self.tpd})
        res = self.tf.getTaskInfo(0, 'percentCompleted')
        self.assertEqual(res, self.tpd)

    def test_get_taskInfo_status(self):
        self.requests_mock.register_uri(
            'GET',
            BASEURL + 'runs/' + self.uuid + '/tasks/0' + '?info=status',
            json={'status': self.status})
        res = self.tf.getTaskInfo(0, 'status')
        self.assertEqual(res, self.status)

    def test_get_taskInfo_all(self):
        info = {
            'percentDone': self.tpd,
            'status': self.status}
        self.requests_mock.register_uri(
            'GET',
            BASEURL + 'runs/' + self.uuid + '/tasks/0' + '?info=',
            json=info)
        res = self.tf.getTaskInfo(0, '')
        for k in res:
            self.assertEqual(res[k], info[k])

    def test_set_taskInfo_fail(self):
        with testtools.ExpectedException(RuntimeError):
            self.tf.setTaskInfo(-1, 'blub', 'blah')
        with testtools.ExpectedException(RuntimeError):
            self.tf.setTaskInfo(self.ntasks, 'blub', 'blah')

    def test_set_taskInfo_percent(self):
        self.requests_mock.register_uri(
            'PUT',
            BASEURL + 'runs/' + self.uuid + '/tasks/0',
            status_code=204)
        self.tf.setTaskInfo(0, 'percentDone', 40)

    def test_set_taskInfo_status(self):
        self.requests_mock.register_uri(
            'PUT',
            BASEURL + 'runs/' + self.uuid + '/tasks/0',
            status_code=204)
        self.tf.setTaskInfo(0, 'status', 'done')

    def test_restart(self):
        self.requests_mock.register_uri(
            'POST',
            BASEURL + 'runs/' + self.uuid + '/restart',
            status_code=204)
        self.tf.restart()

    def test_restart_all(self):
        self.requests_mock.register_uri(
            'POST',
            BASEURL + 'runs/' + self.uuid + '/restart',
            status_code=204)
        self.tf.restart(everything=True)

    def test_delete(self):
        self.requests_mock.register_uri(
            'DELETE',
            BASEURL + 'runs/' + self.uuid,
            status_code=204)
        self.tf.delete()


class TestTFWorker(TestTF):

    def setUp(self):
        super(TestTFWorker, self).setUp()
        self.requests_mock.register_uri(
            'GET', BASEURL + 'runs/' + self.uuid,
            json={'uuid': self.uuid,
                  'numTasks': self.ntasks})
        self.requests_mock.register_uri(
            'POST', BASEURL + 'worker',
            status_code=201)
        self.tf = taskfarm_worker.TaskFarmWorker(
            'user', 'pw', url_base=BASEURL, uuid=self.uuid)

    def test_task(self):
        # make sure there is currently no task
        self.assertIs(self.tf._task, None)

        self.requests_mock.register_uri(
            'POST', BASEURL + 'runs/' + self.uuid + '/task',
            status_code=201,
            json={'task': 0})
        self.requests_mock.register_uri(
            'GET',
            BASEURL + 'runs/' + self.uuid + '/tasks/0'
            '?info=percentCompleted',
            json={'percentCompleted': self.tpd})

        # get a new task
        res = self.tf.task

        self.assertEqual(res, 0)
        self.assertEqual(self.tf._task, 0)

    def test_task_all_done(self):
        # make sure there is currently no task
        self.assertIs(self.tf._task, None)

        self.requests_mock.register_uri(
            'POST', BASEURL + 'runs/' + self.uuid + '/task',
            status_code=204)

        # get a new task
        res = self.tf.task

        self.assertIs(res, None)
        self.assertIs(self.tf._task, None)

    def test_task_update_fail(self):
        self.test_task()

        with testtools.ExpectedException(ValueError):
            self.tf.update(-1)
        with testtools.ExpectedException(ValueError):
            self.tf.update(101)

    def test_task_update(self):
        self.test_task()
        pd = 100

        self.requests_mock.register_uri(
            'PUT',
            BASEURL + 'runs/' + self.uuid + '/tasks/0',
            status_code=204)

        self.tf.update(pd)
        self.assertEqual(self.tf._percentageDone, pd)

    def test_task_done(self):
        self.test_task_update()
        self.tf.done()
        self.assertIs(self.tf._task, None)

    def test_tasks(self):
        # make sure there is currently no task
        self.assertIs(self.tf._task, None)

        responses = []
        for i in range(self.ntasks):
            responses.append({'status_code': 201, 'json': {'task': i}})
            self.requests_mock.register_uri(
                'GET',
                BASEURL + 'runs/' + self.uuid + f'/tasks/{i}'
                '?info=percentCompleted',
                json={'percentCompleted': self.tpd})
            self.requests_mock.register_uri(
                'PUT',
                BASEURL + 'runs/' + self.uuid + f'/tasks/{i}',
                status_code=204)
        responses.append({'status_code': 204})

        self.requests_mock.register_uri(
            'POST', BASEURL + 'runs/' + self.uuid + '/task', responses)

        tasks = []
        for task in self.tf.tasks:
            tasks.append(task)
            self.tf.done()

        for i in range(self.ntasks):
            self.assertEqual(i, tasks[i])
