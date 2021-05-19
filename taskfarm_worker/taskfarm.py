__all__ = ['tfRuns', 'TaskFarm', 'TaskFarmWorker']

import socket
import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.auth import HTTPBasicAuth
from uuid import uuid1


def tfRuns(username, password, url_base='http://localhost:5000/api/'):
    """get a list of runs

    :param username: username for connecting to taskfarm server
    :type username: str
    :param password: password for connecting to taskfarm server
    :type password: str
    :param url_base: base URL for taskfarm server API,
                     defaults to 'http://localhost:5000/api/'
    :type url_base: str

    :return: list of runs
    :rtype: dict
    """
    auth = HTTPBasicAuth(username, password)
    response = requests.get(url_base + 'runs', auth=auth)
    if response.status_code != 200:
        raise RuntimeError('[HTTP {0}]: Content: {1}'.format(
            response.status_code, response.content))
    return response.json()['data']


class TaskFarm:
    """a run consisting of a number of tasks

    :param username: username for connecting to taskfarm server
    :type username: str
    :param password: password for connecting to taskfarm server
    :type password: str
    :param url_base: base URL for taskfarm server API,
                     defaults to 'http://localhost:5000/api/'
    :type url_base: str
    :param uuid: when specified load existing run with uuid
    :type uuid: str
    :param numTasks: create a new run wtih numTasks tasks
    :type numTasks: int

    Intantiate a TaskFarm object with either a uuid to load an
    existing run from the database or create a new run by specifying
    the number of tasks.

    """
    def __init__(self, username, password, uuid=None,
                 numTasks=None, url_base='http://localhost:5000/api/'):
        """constructor"""
        self._url_base = url_base
        self._tauth = None
        self._session = requests.Session()

        # setup session
        # from: https://www.peterbe.com/plog/best-practice-with-retries-with-requests  # noqa E501
        retries = 10
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 503, 504)
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount(url_base, adapter)

        # get a token
        response = self.session.get(
            self.url('token'), auth=HTTPBasicAuth(username, password))

        if response.status_code != 200:
            raise RuntimeError('[HTTP {0}]: Content: {1}'.format(
                response.status_code, response.content))
        self._token = response.json()['token']

        if uuid is None:
            if numTasks is None:
                raise RuntimeError('numTasks must be set '
                                   'when creating a new task')
            response = self.session.post(
                self.url('run'), json={"numTasks": numTasks},
                auth=self.token_auth)
            if response.status_code != 201:
                raise RuntimeError('[HTTP {0}]: Content: {1}'.format(
                    response.status_code, response.content))
            self._uuid = response.json()['uuid']
            self._numTasks = numTasks
        else:
            response = self.session.get(self.url('runs/' + uuid),
                                        auth=self.token_auth)
            if response.status_code != 200:
                raise RuntimeError('[HTTP {0}]: Content: {1}'.format(
                    response.status_code, response.content))
            self._uuid = response.json()['uuid']
            self._numTasks = response.json()['numTasks']

    def url(self, url):
        """construct URL to call

        :param url: url end point
        :type url: str
        :returns: full URL
        :rtype: str

        construct full URL by appending url to url_base
        """
        return '{0}{1}'.format(self._url_base, url)

    @property
    def session(self):
        """the request session"""
        return self._session

    @property
    def token_auth(self):
        """the auth token"""
        if self._tauth is None:
            self._tauth = HTTPBasicAuth(self._token, '')
        return self._tauth

    @property
    def uuid(self):
        """uuid of the run"""
        return self._uuid

    @property
    def numTasks(self):
        """the number of tasks"""
        return self._numTasks

    def info(self, info):
        """get run information

        :param info: the information to query
        :type info: str
        """
        response = self.session.get(
            self.url('runs/' + self.uuid),
            params={'info': info}, auth=self.token_auth)
        if response.status_code != 200:
            raise RuntimeError('[HTTP {0}]: Content: {1}'.format(
                response.status_code, response.content))

        if info == '':
            return response.json()
        else:
            return response.json()[info]

    @property
    def percentDone(self):
        """percentage completed of the run"""
        return self.info('percentDone')

    @property
    def numDone(self):
        """the number of completed tasks"""
        return self.info('numDone')

    @property
    def numWaiting(self):
        """the number of waiting tasks"""
        return self.info('numWaiting')

    @property
    def numComputing(self):
        """the number of tasks being computed"""
        return self.info('numComputing')

    def getTaskInfo(self, task, info):
        """get information about a single task

        :param task: the task ID to query
        :type task: int
        :param info: the information to query
        :type info: str
        """
        if task < 0 or task >= self.numTasks:
            raise RuntimeError(f'task ID outside range 0 {self.numTasks-1}')
        response = self.session.get(
            self.url('runs/' + self.uuid + '/tasks/' + str(task)),
            params={'info': info}, auth=self.token_auth)
        if response.status_code != 200:
            raise RuntimeError('[HTTP {0}]: Content: {1}'.format(
                response.status_code, response.content))

        if info != '':
            return response.json()[info]
        else:
            return response.json()

    def setTaskInfo(self, task, info, value):
        """set information about a single task

        :param task: the task ID to change
        :type task: int
        :param info: the information to change
        :type info: str
        :param value: the value to set it to
        """
        if task < 0 or task >= self.numTasks:
            raise RuntimeError(f'task ID outside range 0 {self.numTasks-1}')
        data = {info: value}
        response = self.session.put(
            self.url('runs/' + self.uuid + '/tasks/' + str(task)),
            json=data, auth=self.token_auth)
        if response.status_code != 204:
            raise RuntimeError('[HTTP {0}]: Content: {1}'.format(
                response.status_code, response.content))

    def restart(self, everything=False):
        """restart run

        :param everything: when set to True reset all tasks even completed
                           ones, default set to False
        :type everything: bool

        The taskfarm does not automaticcaly restart failed tasks.
        Use this method to restart tasks that are marked computing.
        Only restart a run when no more workers are computing.
        """
        data = {'all': str(everything)}
        response = self.session.post(
            self.url('runs/' + self.uuid + '/restart'),
            params=data, auth=self.token_auth)
        if response.status_code != 204:
            raise RuntimeError('[HTTP {0}]: Content: {1}'.format(
                response.status_code, response.content))

    def delete(self):
        """delete run"""
        response = self.session.delete(self.url('runs/' + self.uuid),
                                       auth=self.token_auth)
        if response.status_code != 204:
            raise RuntimeError('[HTTP {0}]: Content: {1}'.format(
                response.status_code, response.content))


class TaskFarmWorker(TaskFarm):
    """
    taskfarm worker object

    :param username: username for connecting to taskfarm server
    :type username: str
    :param password: password for connecting to taskfarm server
    :type password: str
    :param url_base: base URL for taskfarm server API,
                     defaults to 'http://localhost:5000/api/'
    :type url_base: str
    :param uuid: when specified load existing run with uuid
    :type uuid: str

    The taskfarm worker is initialised with the UUID of a run.
    It provides an interface to the tasks associated with the run.

    """
    def __init__(self, username, password, uuid,
                 url_base='http://localhost:5000/api/'):
        """constructor"""

        TaskFarm.__init__(self, username, password,
                          uuid=uuid, url_base=url_base)

        self._task = None
        self._percentageDone = None

        # register worker
        worker = {
            "uuid": uuid1().hex,
            "hostname": socket.gethostname(),
            "pid": os.getpid(),
        }

        response = self.session.post(self.url('worker'),
                                     json=worker, auth=self.token_auth)

        if response.status_code != 201:
            raise RuntimeError('[HTTP {0}]: Content: {1}'.format(
                response.status_code, response.content))

        self._worker_uuid = worker['uuid']

    @property
    def worker_uuid(self):
        """the UUID of the worker"""
        return self._worker_uuid

    @property
    def task(self):
        """the current task associated with the worker

        If there is no task associated with the worker request a new
        task. Return None if there are no more tasks.
        """
        if self._task is None:
            self._percentageDone = None
            worker = {'worker_uuid': self.worker_uuid}
            response = self.session.post(
                self.url('runs/' + self.uuid + '/task'),
                json=worker, auth=self.token_auth)
            if response.status_code == 204:
                # no more tasks
                return self._task
            if response.status_code != 201:
                raise RuntimeError('[HTTP {0}]: Content: {1}'.format(
                    response.status_code, response.content))
            self._task = response.json()['task']
            self._percentageDone = self.getTaskInfo(self._task,
                                                    'percentCompleted')
        return self._task

    @property
    def tasks(self):
        """iterator over all remaining tasks"""
        while self.task is not None:
            yield self.task

    def update(self, percentage):
        """update percentage done of current task

        :param percentage: the value of the percentage done, must be
                           between 0 and 100
        :type percentage: float
        """
        if self._task is None:
            return
        if percentage < 0 or percentage > 100:
            raise ValueError('percentage {} out of range'.format(percentage))
        self._percentageDone = percentage
        self.setTaskInfo(self._task, 'percentCompleted', percentage)

    def done(self):
        """release task

        The task is only marked as done if the percentage done is set to 100.
        """
        if self._task is not None:
            if self._percentageDone is not None and \
               abs(self._percentageDone - 100) < 1e-6:
                self.setTaskInfo(self._task, 'status', 'done')
            self._task = None
