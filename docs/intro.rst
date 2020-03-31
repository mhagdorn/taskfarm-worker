Introduction
============
The taskfarm is a server-client application that tracks tasks to be completed. The server is provides a REST API to create and update runs. This is the python client documentation.


Terminology
-----------

run
  A *run* consists of a number of tasks that need to be completed to solve some problem. A UUID is automatically assigned to a new run. This UUID is used to refer to a particular.
task
  A *task* is a single item of work that forms part of a run. A task is identified by it's number starting from 0 for the first task of a run to numTasks-1 for the last task.

Each task can be in one of the following states:

waiting
  The task is waiting to be scheduled.
computing
  The task is being computed.
done
  The task is finihed.

Tasks also record the percentage completed, the start time and the last updated time. 

Run Administration
------------------
The taskfarm client package comes with a command line run management tool, manageTF.

manageTF supports the following options:
  -h, --help            show this help message and exit
  -b BASEURL, --baseurl BASEURL  API url
  -u USER, --user USER  the taskfarm user
  -p PASSWORD, --password PASSWORD  the password of the taskfarm user
  --list, -l            list all runs
  --info, -i            get info about run
  --reset, -r           reset not completed tasks
  --reset-all, -R       reset all tasks
  --delete, -d          delete run

Use the options -b, -u and -p to connect to the taskfarm server.

Use -l, --list to get a list of all runs. Get the total percentage completed and the number of waiting, computing and done tasks using the option -i, --info.

You can mark all tasks in the computing state as waiting using the -r, --reset option. This is useful when some tasks crashed due to, for example, running out of resources.

You can reset the entire run, ie both computing *and* done tasks using the -R, --reset-all option.

Finally, a run can be deleted using the -d, --delete option.
