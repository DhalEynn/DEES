# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 10:41:59 2020

@author: DhalEynn
"""

from math import floor
from random import randint

# --------------------------- VARIABLES TO CHANGE ------------------------------------

print_console = False
keep_logs = True
# Log level can be "DEBUG" (more detailed), "INFO" (normal) or "WARNING" (only important informations are kept)
log_level = "WARNING"
# Do you use Jupyter Notebook for executing or not
jupyterGraph = False

# Create people from 1 to "nb_of_people"
nb_of_people = 125694
# Duration of the experiment
number_of_months = 3
number_of_days = 1
# number of people who are sick at start
start_sick = 50

# Sleeping time for people
sleepTime = 8

# Average time for an encounter between 2 people, in hours
average_time_of_encounters = 3
# Are encounters hard ?
# False : easy encounters, people are forced to encounters others
# True  : hard encounters, people can encounter nobody when outside
hard_encounters = False
# Percentage of chances of someone available want to go outside
# Used as : if between 0 and max_chances_going_outside  -> go outside
#           if between 61 and max_chances_going_outside -> keep inside for an hour
max_chances_going_outside = 60

# Incubating time of the disease (in days).
# Determinate when you will start being in danger of passing away.
# Possible time is between these 2 values
time_incubating = [0, 8]
# Time before being infectious to others (in days)
time_before_infectious = 1
# Percent of max_infectuosity of the disease.
# Infectuosity can vary between max_infectuosity and "max_infectuosity-20"
max_infectuosity = 80
# Percent of max_lethality of the disease.
max_lethality = 2
# Days before a person can be healed when his disease has incubated
days_before_possible_healing = 0
# Probability to be healed each day from the disease after it has incubated
# Healing chances can vary between healing_chances and "healing_chances-10"
healing_chances = 90
# The immunity of a person to the disease is first taken at random between these bounds.
immunity_bounds = [0, 100]
# If True, randomly increase the immunity of a healed person with a value between immunity_ri_start and immunity_ri_start + immunity_increase.
immunity_random_increase = False
immunity_ri_start = 20
# If a person heal from the disease and immunity_random_increase is False, his immunity is increased flatly by this amount.
# Else, look at immunity_random_increase description
immunity_increase = 50


# --------------------------- DO NOT CHANGE ------------------------------------


def getMaxChancesGoingOutside():
    global max_chances_going_outside
    if (max_chances_going_outside > 100):
        max_chances_going_outside = 100
    if (max_chances_going_outside < 0):
        max_chances_going_outside = 0
    return int(max_chances_going_outside)


def getMaxInfectuosity():
    global max_infectuosity
    if (max_infectuosity > 100):
        max_infectuosity = 100
    if (max_infectuosity < 0):
        max_infectuosity = 0
    if (max_infectuosity < 20):
        return randint(0, max_infectuosity)
    return randint(max_infectuosity - 20, max_infectuosity)


def getMaxLethality():
    global max_lethality
    if (max_lethality > 100):
        max_lethality = 100
    if (max_lethality < 0):
        max_lethality = 0
    return int(max_lethality)


def getHoursBeforeHeal():
    global days_before_possible_healing
    if (days_before_possible_healing < 0):
        days_before_possible_healing = 0
    return int(days_before_possible_healing * 24)


def getHoursBeforeInfectious():
    global time_before_infectious
    if (time_before_infectious < 0):
        time_before_infectious = 0
    return int(time_before_infectious * 24)


def getTimeIncubating():
    global time_incubating
    temp_incubating = [min(time_incubating[0], time_incubating[1]), max(time_incubating[0], time_incubating[1])]
    if (temp_incubating[0] < 0):
        temp_incubating[0] = 0
    if (temp_incubating[1] < 0):
        temp_incubating[1] = 0
    return randint(floor(temp_incubating[0] * 24), floor(temp_incubating[1] * 24))


def getHealingChances():
    global healing_chances
    if (healing_chances > 100):
        healing_chances = 100
    if (healing_chances < 0):
        healing_chances = 0
    if (healing_chances < 10):
        return randint(0, healing_chances)
    return randint(healing_chances - 10, healing_chances)


def getImmunity():
    global immunity_bounds
    immunity = randint(immunity_bounds[0], immunity_bounds[1])
    if (immunity > 100):
        immunity = 100
    if (immunity < 0):
        immunity = 0
    return immunity


def getIncreasedImmunity(old_immunity):
    if (old_immunity >= 100):
        return 100
    global immunity_ri_start, immunity_increase, immunity_random_increase
    if (immunity_random_increase):
        temp = old_immunity + \
            randint(immunity_ri_start, immunity_ri_start + immunity_increase)
    else:
        temp = old_immunity + immunity_increase
    if (temp > 100):
        temp = 100
    if (temp < 0):
        temp = 0
    return temp


# Number of days of the experience
lenght_experiment = number_of_months * 30 + \
    floor(number_of_months / 2) + \
    number_of_days


if (time_before_infectious < 0):
    time_before_infectious = 0

if (average_time_of_encounters < 0):
    average_time_of_encounters = 0
