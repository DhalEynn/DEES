# DEES
    A Discret Element Epidemic Simulator with Python using simpy.
    By DahlEynn

# How to use :

1. Change whatever variables you want in variables.py
2. Launch main.py

# Main library used :

* Plotly : `pip install plotly`
* SimPy : `pip install simpy`


# Some informations :

* Be careful with the logs. With my example of 124k person, and with minimal (warning only) logs, I still had a 400Mo file of logs at the end of the 92 days of test. More detailed logs make for a very big file and a long time of execution.
* If you use a Jupyter Notebook, you can print the graph directly in your console by putting the jupyterGraph variable (in variables.py) at True.


# Tested with :
* Windows 10 x64, Education edition
* Python 3.7.4 64-bit, base Conda

* Settings : 92 days for 50000 people, 500 sick people, 2% death rate, 90% healing chances, easy encounters, no logs
* Result : 6.30min execution time, a graph. Disease eradicated at 54 days, 19865 healthy people, 29895 immune people (100% immunity), 0 sick people, 240 dead people.

* Settings : 92 days for 50000 people, 5000 sick people, 2% death rate, 90% healing chances, easy encounters, no logs
* Result : 5.51min execution time, a graph. Disease eradicated at 51 days, 19276 healthy people, 30470 immune people (100% immunity), 0 sick people, 254 dead people.