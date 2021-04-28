#!/bin/env python

from taskfarm_worker import TaskFarm
from taskfarm_worker import TaskFarmWorker
import time
import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--baseurl', default="http://localhost:5000/api/",
                    help='API url')
parser.add_argument('-u', '--user', default='dhdt', help="the taskfarm user")
parser.add_argument('-p', '--password', default='hello',
                    help="the password of the taskfarm user")
parser.add_argument('-n', '--num-tasks', type=int, default=10,
                    help="set the number of tasks")
parser.add_argument('--uuid', help="the UUID of the run")

args = parser.parse_args()

if args.uuid is None:
    # create a new run
    tf = TaskFarm(args.user, args.password, numTasks=args.num_tasks,
                  url_base=args.baseurl)
    print(tf.uuid)
else:
    tf = TaskFarmWorker(args.user, args.password, args.uuid,
                        url_base=args.baseurl)
    print(tf.percentDone)

    for t in tf.tasks:
        print("worker {} processing task {}".format(tf.worker_uuid, t))
        for i in range(1, 11):
            time.sleep(random.randrange(1, 15) / 10.)
            tf.update(i * 10)
        tf.done()
