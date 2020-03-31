Using the Taskfarm Client
=========================

Setting up a run
----------------
You can create a new run by intantiating a ``TaskFarm`` object:

.. code-block:: python
		
 run = TaskFarm('user','secret',numTasks=10,
               url_base='http://localhost:5000/api/')

creates are run with 10 tasks. The Taskfarm user and password need to specified as well as the URL of the service.

You can get a list of existing runs:

.. code-block:: python

 runs = tfRuns('user','secret,
              url_base='http://localhost:5000/api/')

You can also intantiate an ``TaskFarm`` object given the UUID of a run:

.. code-block:: python

 run = TaskFarm('user','secret',
               uuid='da8eb1c10eac4cefb39c8889d6d7170a',
               url_base='http://localhost:5000/api/')

A Taskfarm Worker
-----------------
Once you have a run with some tasks you can create a worker like this

.. code-block:: python

    tf = TaskFarmWorker('user','secret',
               'da8eb1c10eac4cefb39c8889d6d7170a',
               url_base='http://localhost:5000/api/')
    print (tf.percentDone)

    for t in tf.tasks:
        print ("worker {} processing task {}"
	       .format(tf.worker_uuid,t))
	# do some work
	# update the percentage done
        tf.update(50)
	# do some more work and update percentage
	tf.update(100)
	# mark task as completed
        tf.done()
