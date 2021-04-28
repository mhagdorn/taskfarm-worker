import argparse
from taskfarm_worker import TaskFarm, tfRuns


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--baseurl',
                        default="http://localhost:5000/api/", help='API url')
    parser.add_argument('uuid', nargs='?', help="run UUID")
    parser.add_argument('-u', '--user', default='dhdt',
                        help="the taskfarm user")
    parser.add_argument('-p', '--password', default='hello',
                        help="the password of the taskfarm user")
    main_modes = parser.add_mutually_exclusive_group()
    main_modes.add_argument('--list', '-l', action='store_true',
                            default=False, help="list all runs")
    main_modes.add_argument('--info', '-i', action='store_true',
                            default=False, help="get info about run")
    main_modes.add_argument('--reset', '-r', action='store_true',
                            default=False, help="reset not completed tasks")
    main_modes.add_argument('--reset-all', '-R', action='store_true',
                            default=False, help="reset all tasks")
    main_modes.add_argument('--delete', '-d', action='store_true',
                            default=False, help="delete run")
    args = parser.parse_args()

    if args.list:
        for r in tfRuns(args.user, args.password, url_base=args.baseurl):
            print("{run[id]} {run[uuid]} {run[numTasks]}".format(run=r))
    else:
        if args.uuid is None:
            parser.error('No run UUID specified')

        tf = TaskFarm(args.user, args.password, uuid=args.uuid,
                      url_base=args.baseurl)
        if args.info:
            print("{info[id]} {info[uuid]} {info[numTasks]} "
                  "({info[numWaiting]},{info[numComputing]},{info[numDone]}) "
                  "{info[percentDone]}".format(info=tf.info('')))
        elif args.reset_all:
            tf.restart(everything=True)
        elif args.reset:
            tf.restart()
        elif args.delete:
            tf.delete()


if __name__ == '__main__':
    main()
