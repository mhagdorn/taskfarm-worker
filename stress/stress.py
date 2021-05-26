#!/bin/env python

from taskfarm_worker import TaskFarm, TaskFarmWorker
import time
import argparse
import multiprocessing
import pandas


def worker(user, password, url_base, uuid):
    tf = TaskFarmWorker(user, password, uuid,
                        url_base=url_base)

    print(f'starting worker {tf.worker_uuid}')

    nTasks = 0
    totalCheckout = 0.
    totalUpdate = 0.
    totalDone = 0.

    ta = time.time()
    for t in tf.tasks:
        tb = time.time()
        nTasks += 1
        totalCheckout += tb - ta

        for i in range(1, 11):
            ta = time.time()
            tf.update(i * 10)
            tb = time.time()
            totalUpdate += tb - ta
        ta = time.time()
        tf.done()
        tb = time.time()
        totalDone += tb - ta
        ta = time.time()

    total = totalCheckout + totalUpdate + totalDone
    results = (tf.worker_uuid, nTasks, total, totalCheckout / nTasks,
               totalUpdate / (10 * nTasks), totalDone / nTasks)

    return results


def stress(user, password, url_base, numTasks, nThreads, nWorkers=None):
    # create a new run
    tf = TaskFarm(user, password, numTasks=numTasks, url_base=url_base)

    # create tasks
    tasks = [(user, password, url_base, tf.uuid)] * nThreads

    cols = ['client', 'ntasks', 'total', 'getTask', 'updateTask', 'doneTask']

    with multiprocessing.Pool(processes=nThreads) as pool:
        res = pool.starmap_async(worker, tasks)

        pool.close()

        timings = pandas.DataFrame(res.get(), columns=cols)

    timings['nClients'] = [nThreads] * nThreads
    if nWorkers is not None:
        timings['nWorkers'] = [nWorkers] * nThreads
    timings.set_index('client', inplace=True)
    tf.delete()

    return timings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--baseurl',
                        default="http://localhost:5000/api/", help='API url')
    parser.add_argument('-u', '--user', default='dhdt',
                        help="the taskfarm user")
    parser.add_argument('-p', '--password', default='hello',
                        help="the password of the taskfarm user")
    parser.add_argument('-n', '--num-tasks', type=int, default=256,
                        help="set the number of tasks")
    parser.add_argument('-N', '--num-workers', type=int,
                        help="set the number of workers used by the taskfarm"
                        " server. This is only use for info")
    parser.add_argument('-o', '--output', metavar='FILE',
                        help="store results as CSV in FILE")

    args = parser.parse_args()

    timings = []
    nWorkers = [1, 2, 4, 8, 16, 32, 64]

    for n in nWorkers:
        t = stress(args.user, args.password, args.baseurl,
                   args.num_tasks, n, nWorkers=args.num_workers)
        timings.append(t.mean())

    timings = pandas.DataFrame(timings)
    if args.output is not None:
        timings.to_csv(args.output)
    else:
        print(timings)


if __name__ == '__main__':
    main()
