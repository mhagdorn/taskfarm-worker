Simple Example
==============
The repository contains a simple `example script <https://github.com/mhagdorn/taskfarm-worker/blob/master/example.py>`_ that demonstrates the functionality of the taskfarm system. The script either creates a new *run* or it processes tasks of an existing run. The example tasks merely consist of sleeping for a random duration.

Assuming you have followed the server `installation instructions <https://taskfarm.readthedocs.io/en/latest/installation.html#containerised-installation>`_ and are running the taskfarm service on the local host in a docker container you can create a new run with 20 tasks

.. code-block:: bash
                
  python example.py -b http://localhost/api/ -u taskfarm -p hello -n 20

This command returns the UUID of the run it has just created. You can now use the the :ref:`admin command <Run Administration>` to watch the progress of a run 

.. code-block:: bash
                
  watch manageTF -b http://localhost/api/ -u taskfarm -p hello -i 7aceaed8733d4d2f89a7f3f1e3ed6b1f

You can now start some workers. For example you can start 5 workers using

.. code-block:: bash
                
  for i in $(seq 5); do
    python example.py -b http://localhost/api/ -u taskfarm -p hello --uuid 7aceaed8733d4d2f89a7f3f1e3ed6b1f &
  done

Each worker requests a new task from the server, processes it and once completed it marks it as done. It then requests new tasks until all tasks are completed.
