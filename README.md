# DEES
    A Discret Element Epidemic Simulator with Python using simpy.
    By DahlEynn

# How to use :

1. Change whatever variables you want in variables.py
2. Launch main.py


# Some informations :

* Be careful with the logs. With my example of 124k person, and with minimal (warning only) logs, I still had a 400Mo file of logs at the end of the 92 days of test. More detailed logs make for a very big file and a long time of execution.
* If you use a Jupyter Notebook, you can print the graph directly in your console by putting the jupyterGraph variable (in variables.py) at True.


# Tested with :
* Windows 10 x64, Education edition
* Python 3.7.4 64-bit, base Conda

* Settings : 92 days for 124k people, logs in "WARNING" level (important information only)
* Result : 50min execution time, 400Mo of logs and a graph.