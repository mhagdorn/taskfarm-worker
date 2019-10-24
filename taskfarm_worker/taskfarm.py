__all__ = ['tfRuns','TaskFarm','TaskFarmWorker']

import socket
import os
from datetime import datetime
import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.auth import HTTPBasicAuth
from uuid import uuid1

def tfRuns(username,password,url_base='http://localhost:5000/api/'):
    auth = HTTPBasicAuth(username, password)
    response = requests.get(url_base+'runs', auth=auth)
    if response.status_code != 200:
        raise RuntimeError('[HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
    return response.json()['data']
    
class TaskFarm:
    def __init__(self,username,password,uuid = None, numTasks = None,url_base='http://localhost:5000/api/'):
        self._url_base = url_base
        self._tauth = None
        self._session = requests.Session()

        # setup session
        # from: https://www.peterbe.com/plog/best-practice-with-retries-with-requests
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
        response = self.session.get(self.url('token'), auth=HTTPBasicAuth(username, password))

        if response.status_code != 200:
            raise RuntimeError('[HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
        self._token = response.json()['token']

        if uuid is None:
            if numTasks == None:
                raise RuntimeError('numTasks must be set when creating a new task')
            response = self.session.post(self.url('run'),json=json.dumps({"numTasks":numTasks}),auth=self.token_auth)
            if response.status_code != 201:
                raise RuntimeError('[HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
            self._uuid = response.json()['uuid']
            self._numTasks = numTasks
        else:
            response = self.session.get(self.url('runs/'+uuid),auth=self.token_auth)
            if response.status_code != 200:
                raise RuntimeError('[HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
            self._uuid = response.json()['uuid']
            self._numTasks = response.json()['numTasks']

    def url(self,url):
        return '{0}{1}'.format(self._url_base,url)

    @property
    def session(self):
        return self._session
    
    @property
    def token_auth(self):
        if self._tauth is None:
            self._tauth = HTTPBasicAuth(self._token, '')
        return self._tauth
    
    @property
    def uuid(self):
        return self._uuid
    @property
    def numTasks(self):
        return self._numTasks
    
    def info(self,info):
        response = self.session.get(self.url('runs/'+self.uuid),params={'info':info},auth=self.token_auth)
        if response.status_code != 200:
            raise RuntimeError('[HTTP {0}]: Content: {1}'.format(response.status_code, response.content))

        if info=='':
            return response.json()
        else:
            return response.json()[info]

    @property
    def percentDone(self):
        return self.info('percentDone')
    @property
    def numDone(self):
        return self.info('numDone')
    @property
    def numWaiting(self):
        return self.info('numWaiting')
    @property
    def numComputing(self):
        return self.info('numComputing')

    def getTaskInfo(self,task,info):
        assert task >=0 and task < self.numTasks
        response = self.session.get(self.url('runs/'+self.uuid+'/tasks/'+str(task)),params={'info':info},auth=self.token_auth)
        if response.status_code != 200:
            raise RuntimeError('[HTTP {0}]: Content: {1}'.format(response.status_code, response.content))

        if info != '':
            return response.json()[info]
        else:
            return response.json()

    def setTaskInfo(self,task,info,value):
        assert task >=0 and task < self.numTasks
        data = {info:value}
        response = self.session.put(self.url('runs/'+self.uuid+'/tasks/'+str(task)),json=json.dumps(data),auth=self.token_auth)
        if response.status_code != 204:
            raise RuntimeError('[HTTP {0}]: Content: {1}'.format(response.status_code, response.content))

    def restart(self,everything=False):
        data = {'all':str(everything)}
        response = self.session.post(self.url('runs/'+self.uuid+'/restart'),params=data,auth=self.token_auth)
        if response.status_code != 204:
            raise RuntimeError('[HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
                                
    def delete(self):
        response = self.session.delete(self.url('runs/'+self.uuid),auth=self.token_auth)
        if response.status_code != 204:
            raise RuntimeError('[HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
        
class TaskFarmWorker(TaskFarm):
    def __init__(self,username,password,uuid,url_base='http://localhost:5000/api/'):
        
        TaskFarm.__init__(self,username,password,uuid=uuid,url_base=url_base)

        self._task = None
        self._percentageDone = None
        
        # register worker
        worker = {
            "uuid" : uuid1().hex,
            "hostname" : socket.gethostname(),
            "pid" : os.getpid(),
        }

        response = self.session.post(self.url('worker'),json=json.dumps(worker),auth=self.token_auth)

        if response.status_code != 201:
            raise RuntimeError('[HTTP {0}]: Content: {1}'.format(response.status_code, response.content))

        self._worker_uuid = worker['uuid']

    @property
    def worker_uuid(self):
        return self._worker_uuid
        
    @property
    def task(self):
        if self._task is None:
            self._percentageDone = None
            worker = {'worker_uuid':self.worker_uuid}
            response = self.session.post(self.url('runs/'+self.uuid+'/task'),json=json.dumps(worker),auth=self.token_auth)
            if response.status_code == 204:
                # no more tasks
                return self._task
            if response.status_code != 201:
                raise RuntimeError('[HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
            self._task = response.json()['task']
            self._percentageDone = self.getTaskInfo(self._task,'percentCompleted')
        return self._task

    @property
    def tasks(self):
        while self.task is not None:
            yield self.task

    def update(self,percentage):
        if self._task is None:
            return
        if percentage <0 or percentage > 100:
            raise ValueError('percentage %f out of range'%percentage)
        self._percentageDone = percentage
        self.setTaskInfo(self._task,'percentCompleted',percentage)

    def done(self):
        if self._task is not None:
            if self._percentageDone is not None and abs(self._percentageDone-100) < 1e-6:
                self.setTaskInfo(self._task,'status','done')
            self._task = None
            
if __name__ == '__main__':
    import sys

    if len(sys.argv)>1:
        tf = TaskFarmWorker('dhdt','hello',uuid=sys.argv[1])
        print (tf.uuid)
        print (tf.percentDone)
        print (tf.numWaiting,tf.numDone,tf.numComputing)
        print (tf.worker_uuid)
        for t in tf.tasks:
            print (t)
        for i in range(tf.numTasks):
            print (tf.getTaskInfo(i,''))
            print (tf.getTaskInfo(i,'status'),tf.getTaskInfo(i,'percentCompleted'))
            tf.setTaskInfo(i,'percentCompleted',10.)
    else:
        tf = TaskFarm('dhdt','hello',numTasks=10)
        print (tf.uuid)
        
    
    #tfw = TaskFarmWorker('dhdt','hello')
    #print (tfw.task)
