taskfarm-worker
===============
This package is the client code to work with the [taskfarm](https://github.com/mhagdorn/taskfarm) web application.

You can use the manageTF script to manage the task farm.

Find the full documentation on https://taskfarm-worker.readthedocs.io/

Examples
--------
Have a look at the [example script](../master/example.py) to see how to 
use the module. The [stress/stress.py script](../master/stress/stress.py) 
stresses the taskfarm server by spawning multiple clients. You can use the 
[stress/plot.py script](../master/stress/plot.py) to plot the csv files 
produced by the stress script.

Hagdorn, M. and Gourmelen, N., 2023. Taskfarm: A Client/Server Framework for Supporting Massive Embarrassingly Parallel Workloads. Journal of Open Research Software, 11(1), p.1. DOI: [10.5334/jors.393](http://doi.org/10.5334/jors.393)

[![test package taskfarm-worker](https://github.com/mhagdorn/taskfarm-worker/actions/workflows/pythonapp.yml/badge.svg)](https://github.com/mhagdorn/taskfarm-worker/actions/workflows/pythonapp.yml)[![Documentation Status](https://readthedocs.org/projects/taskfarm-worker/badge/?version=latest)](https://taskfarm-worker.readthedocs.io/en/latest/?badge=latest) [![CITATION.cff](https://github.com/mhagdorn/taskfarm-worker/actions/workflows/cff-validator.yml/badge.svg)](https://github.com/mhagdorn/taskfarm-worker/actions/workflows/cff-validator.yml)

