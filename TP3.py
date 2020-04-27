# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 08:03:50 2020

@author: DhalEynn
"""

import simpy
#import sys
import time
import logging
import os
import variables as const
from random import randint, sample
from datetime import timedelta
from math import ceil


# --------------------------- CLASS PERSON ------------------------------------


class Person(object):
    def __init__(self, name):
        self.name = name

        # Is actually sick (has in has been contaminated by the disease and can potentially transmit it).
        self.is_sick = False
        # Is the person putting himself in self quarantine, meaning that he wont go out until being healed
        self.isSelfQuarantined = False

        self.is_infectious = False  # Can the person transmit the disease ?
        # Period before the person is infectious.
        self.time_before_infectious = const.getHoursBeforeInfectious()
        # Chances to transmit the disease to other people.
        self.infectuosity = const.getMaxInfectuosity()

        # Has the disease reached its incubation threshold (onset of first symptoms / likelihood of dying from the disease) ?
        self.has_incubated = False
        # Incubation period of the disease for this person.
        self.time_incubating = const.getTimeIncubating()

        # Represent the timer used if someone is sick for the following two variables.
        self.hours_before_new_check = -1
        # Number of hours before someone can be healed
        self.hours_before_possible_healing = -1
        # Chances to heal from the disease.
        self.healing_chances = const.getHealingChances()
        # Chances to die from the disease.
        self.chances_to_die = const.getMaxLethality()
        # Chances to be immune from the disease (more precisely, the chances to not be contaminated after contact with a contaminated person).
        self.immunity_chances = const.getImmunity()

        self.is_sleeping = False
        self.time_until_awakening = 0
        self.time_awake = abs(24 - const.sleepTime)

        self.is_outside = False
        self.is_coming_back_home = False
        self.time_until_coming_back = 0

    def __str__(self):
        temp_vars_str = vars(self)
        temp_print_str = ""
        for item in temp_vars_str:
            if (temp_print_str == ""):
                temp_print_str = str(item) + " : " + \
                    str(temp_vars_str[item]) + '\n'
            else:
                temp_print_str += "  " + \
                    str(item) + " : " + str(temp_vars_str[item]) + '\n'
        return temp_print_str
    
    def littleStr(self):
        return " Name : " + str(self.name) + " Is sick : " + str(self.is_sick)


# --------------------------- CLASS PEOPLE ------------------------------------


class People(object):

    def printArray(self, people):
        for person in people:
            print(str(person))

    def printNameForArray(self, people):
        for person in people:
            print(str(person.name))

    # -------------------------- INITIALISATION ---------------------------------

    def __init__(self, env):
        # Start the environnement
        self.env = env

        # Create internal variables
        # List of people
        self.people = []
        # Time passed
        self.time = timedelta(hours=0)
        # Fill the people array
        for value in range(1, const.nb_of_people + 1):
            self.people.append(Person("Personne " + str(value)))
        # Create the variables for the graphs
        self.nb_sick = 0
        self.nb_dead = 0
        # Make some people sick
        for person in sample(self.people, const.start_sick):
            person.is_sick = True
            self.nb_sick += 1

        # Start the run process.
        self.action = env.process(self.run())

    # -------------------------- SLEEP ---------------------------------

    def shouldAwakenIndexed(self, index):
        """Should the person awaken (use the index of self.people)"""
        person = self.people[index]
        if (person.is_sleeping == True):
            person.time_until_awakening -= 1
            if (person.time_until_awakening <= 0):
                person.is_sleeping = False
                person.time_until_awakening = 0
                logText('at %s, %s is now awake' %
                        (self.time, person.name), "info")
            else:
                logText('at %s, %s is now %d hours from awakening' % (
                    self.time, person.name, person.time_until_awakening), "debug")

    def shouldAwaken(self, person):
        """Should the person awaken"""
        if (person.is_sleeping == True):
            person.time_until_awakening -= 1
            if (person.time_until_awakening <= 0):
                person.is_sleeping = False
                person.time_until_awakening = 0
                logText('at %s, %s is now awake' %
                        (self.time, person.name), "info")
            else:
                logText('at %s, %s is now %d hours from awakening' % (
                    self.time, person.name, person.time_until_awakening), "debug")

    def goToSleepIndexed(self, index):
        """Put the person to sleep (if awake) using the index of self.people"""
        person = self.people[index]
        if (person.is_sleeping != True):
            person.is_sleeping = True
            person.time_until_awakening = abs(const.sleepTime)
            person.time_awake = 0
            logText('at %s, %s is going to sleep for %d hours' %
                    (self.time, person.name, person.time_until_awakening), "info")

    def goToSleep(self, person):
        """Put the person to sleep (if awake)"""
        if (person.is_sleeping != True):
            person.is_sleeping = True
            person.time_until_awakening = abs(const.sleepTime)
            person.time_awake = 0
            logText('at %s, %s is going to sleep for %d hours' %
                    (self.time, person.name, person.time_until_awakening), "info")

    def addingAwakeTime(self, person):
        """Update the time a person has been awake"""
        if (person.is_sleeping != True):
            person.time_awake += 1

    def sleepChances(self, person):
        """Return the chances to put person to sleep

        Give you the chances of puting someone to sleep depending on the amount of time they were awake.
        Return is proportional : 0%    at 0 hours
                                 50%   at 24 - const.sleepTime
                                 100%  at (24 - const.sleepTime) * 2
        """

        return ceil(person.time_awake * 50 / abs(24 - const.sleepTime))

    # ------------------------ ENCOUNTERS ---------------------------------

    # Should the person go back to his house

    def shouldGoBackHome(self, person):
        if (person.is_outside == True):
            person.time_until_coming_back -= 1
            if (person.time_until_coming_back <= 0):
                person.is_outside = False
                person.is_coming_back_home = True
                person.time_until_coming_back = 0
                logText('at %s, %s is now back home' %
                        (self.time, person.name), "info")
            else:
                logText('at %s, %s is currenty staying outside for another %d hours' % (
                    self.time, person.name, person.time_until_coming_back), "debug")

    def isEncountering(self, person1, person2):
        person1.is_outside = True
        person2.is_outside = True

        time_of_encounter = const.average_time_of_encounters + randint(-1, 1)
        if (time_of_encounter < 1):
            time_of_encounter = 1
        person1.time_until_coming_back = time_of_encounter
        person2.time_until_coming_back = time_of_encounter

        logText("at %s, %s will encounter %s for %d hours" % (
            self.time, person1.name, person2.name, time_of_encounter), "info")
        self.shouldContaminate(person1, person2)

    def easyEncounters(self):
        while (len(self.dynamic_available) > 1):
            two_people = sample(range(len(self.dynamic_available)), 2)
            two_people.sort()
            self.isEncountering(self.dynamic_available[two_people[0]], self.dynamic_available[two_people[1]])
            del self.dynamic_available[two_people[1]]
            del self.dynamic_available[two_people[0]]
        if (len(self.dynamic_available) == 1):
            logText("at %s, %s encountered no one when going out" %
                    (self.time, self.dynamic_available[0].name), "debug")

    def hardEncounters(self):
        print("Hard encounters")  # Fonction a créer

    # ------------------------ SICKNESS ---------------------------------

    def isInfectious(self, person):
        if (person.is_sick == True and person.is_infectious == False):
            if (person.time_before_infectious < 1):
                logText('at %s, %s can now transmit the disease.' %
                        (self.time, person.name), "info")
                person.is_infectious = True
            else:
                logText('at %s, %s is now %d hours from being infectious.' % (
                    self.time, person.name, person.time_before_infectious), "debug")
                person.time_before_infectious -= 1

    def shouldContaminate(self, person1, person2):
        if (not (person1.is_sick == True and person2.is_sick == True) and (person1.is_sick == True or person2.is_sick == True)):
            if (person1.is_infectious == True or person2.is_infectious == True):  # Is the sick person infectious ?
                rand_chance_to_be_contaminated = randint(0, 100)
                if (person1.is_infectious == True and person2.is_sick == False):
                    # Has person1 transmited the disease (via speaking, touching, etc) to person 2 ?
                    if (rand_chance_to_be_contaminated < person1.infectuosity):
                        # Has person2 been contaminated by person 1 or has person2 immunity stopped contamination
                        if (randint(0, 100) < person2.immunity_chances):
                            person2.is_sick = True
                            self.nb_sick += 1
                            logText("at %s, %s has been contaminated by %s." % (self.time, person2.name, person1.name), "info")
                            logText('at %s, %s is now sick.' % (self.time, person2.name), "warn")
                            logText('at %s, nb_sick : %d' % (self.time, self.nb_sick), "warn")
                if (person2.is_infectious == True and person1.is_sick == False):
                    if (rand_chance_to_be_contaminated < person2.infectuosity):
                        if (randint(0, 100) < person1.immunity_chances):
                            person1.is_sick = True
                            self.nb_sick += 1
                            logText("at %s, %s has been contaminated by %s." % (self.time, person1.name, person2.name), "info")
                            logText('at %s, %s is now sick.' % (self.time, person1.name), "warn")
                            logText('at %s, nb_sick : %d' % (self.time, self.nb_sick), "warn")

    def hasIncubated(self, person):
        if (person.is_sick == True and person.has_incubated == False):
            if (person.time_incubating < 1):
                logText('at %s, %s disease has now incubated' %
                        (self.time, person.name), "info")
                person.has_incubated = True
                person.hours_before_new_check = 24
                person.hours_before_possible_healing = const.getHoursBeforeHeal()
            else:
                logText('at %s, %s disease is now %d hours from incubating' % (
                    self.time, person.name, person.time_incubating), "debug")
                person.time_incubating -= 1

    def shouldHeal(self, person):
        if (person.is_sick == True and person.has_incubated == True):
            if (person.hours_before_possible_healing > 0 and person.hours_before_possible_healing != -1):
                person.hours_before_possible_healing -= 1
            else:
                person.hours_before_possible_healing += 24
                rand_chance_to_heal = randint(0, 100)
                if (rand_chance_to_heal < person.healing_chances):
                    logText('at %s, %s disease is now cured' %
                            (self.time, person.name), "warn")
                    person.is_sick = False
                    person.is_infectious = False
                    person.has_incubated = False
                    self.nb_sick -= 1
                    logText('at %s, nb_sick : %d' % (self.time, self.nb_sick), "warn")
                    person.hours_before_new_check = -1
                    person.hours_before_possible_healing = -1
                    person.immunity_chances = const.getIncreasedImmunity(person.immunity_chances)
                    person.time_before_infectious = const.getHoursBeforeInfectious()
                    person.time_incubating = const.getTimeIncubating()

    def shouldDie(self, person):
        if (person.is_sick == True):
            rand_chance_to_die = randint(0, 100)
            if (rand_chance_to_die < person.chances_to_die):
                logText('at %s, %s died from the disease.' % (self.time, person.name), "warn")
                return True
        return False
    
    def advenceCheck(self, person):
        if (person.hours_before_new_check == 0):
            person.hours_before_new_check = 24
        if (person.hours_before_new_check != -1):
            person.hours_before_new_check -= 1

    # ------------------------ OTHER ---------------------------------

    def isAvailable(self, person):
        if (person.is_sleeping == True):
            return False
        if (person.is_outside == True):
            return False
        # Person is coming back to his home, so is not available for going outside again this hour
        if (person.is_coming_back_home == True):
            person.is_coming_back_home = False
            return False
        return True

    def detailedActions(self, person):
        if (self.isAvailable(person)):
            # Look if the person want to go to sleep
            if (randint(0, 100) < self.sleepChances(person)):
                self.goToSleep(person)
            # If the person don't want to go to sleep
            # Look at if the person want to go outside
            elif (randint(0, 100) < const.max_chances_going_outside):
                self.dynamic_available.append(person)
                logText("at %s, %s is going outside." %
                        (self.time, person.name), "info")
            else:
                logText("at %s, %s is staying at home for now." %
                        (self.time, person.name), "info")
    
    def dailyCounter(self):
        """What is done "daily", as in each 24 hours."""
        global temp_time
        if (self.env.now % (24) == 0):
            print("Elapsed real time : %s" % str(timedelta(seconds=(time.time() - temp_time))))
            temp_time = time.time()
            print("Timeline : %s" % str(self.time))
            self.graph_array.append({"day" : int(self.env.now / 24), "healthy_people" : const.nb_of_people - self.nb_dead - self.nb_sick, "deaths" : self.nb_dead, "sick" : self.nb_sick})

    # ------------------------ MAIN ---------------------------------

    def run(self):
        while True:
            self.time = timedelta(hours=self.env.now)

            self.dailyCounter()

            # If nobody is sick anymore, the disease has been eradicated
            if (self.nb_sick <= 0):
                print("at %s, the disease has been eradicated." % (self.time))
                logText("at %s, the disease has been eradicated." % (self.time), "warn")
                while True:
                    self.dailyCounter()
                    # Advance the time of the simulation by one hour
                    yield self.env.timeout(1)

            # List of people who will die this day
            self.dead_people = []
            # List of people who are available for encounters
            self.dynamic_available = []
            for person in self.people:
                alive = True
                self.advenceCheck(person)
                if (person.hours_before_new_check != -1):
                    if (person.hours_before_new_check == 0):
                        if (self.shouldDie(person)):
                            self.dead_people.append(person)
                            alive = False
                            self.nb_dead += 1
                            self.nb_sick -= 1
                            logText('at %s, nb_sick : %d' % (self.time, self.nb_sick), "warn")
                if(alive):
                    self.shouldHeal(person)
                    self.isInfectious(person)
                    self.hasIncubated(person)
                    self.addingAwakeTime(person)
                    self.shouldAwaken(person)
                    self.shouldGoBackHome(person)
                    self.detailedActions(person)
                
            if (len(self.dead_people) != 0):
                self.people = difference_lists(self.people, self.dead_people)

            if (const.hard_encounters):
                self.hardEncounters()
            else:
                self.easyEncounters()

            # Advance the time of the simulation by one hour
            yield self.env.timeout(1)


# -------------------------- OTHER FUNCTIONS ----------------------------------


def logText(text, log_type):
    """Log function, with log type input"""
    if(const.print_console):
        print(str(text))
    if(const.keep_logs):
        if (log_type.lower() == "info"):
            logging.info(str(text))
        elif (log_type.lower() == "debug"):
            logging.debug(str(text))
        elif (log_type.lower() == "warn"):
            logging.warning(str(text))
        else:
            logging.error("WTF is that : " + text + " " + log_type)


def writeArray(people, log_type):
    if (const.nb_of_people < 1000):
        for person in people:
            logText(str(person), log_type)
    else:
        for person in people:
            logText(person.littleStr(), log_type)


def difference_lists(first, second):
    """Function that return the difference between 2 lists.
    
    This function will return the difference between two lists, first and second.
    More exaustively, it will return a list of all the items that are in the first list
    and aren't in the second list.
    I use the set() function on the second member only to keep the order and repetitions of the first list.
    For more infos : https://stackoverflow.com/questions/6486450/python-compute-list-difference/6486467
    """

    second = set(second)
    return [item for item in first if item not in second]

def percentPeople(value):
    """Return the percentage that value represent in all the people"""
    return (value * 100) / const.nb_of_people

def print_graph(grouping):
    """Function that print the evolution of the disease."""
    list_days = []
    list_people = []
    hover_people = []
    list_death = []
    hover_death = []
    list_sick = []
    hover_sick = []
    print("Printing graph")
    for item in grouping:
        list_days.append(item["day"])
        list_people.append(item["healthy_people"])
        hover_people.append("Day " + str(item["day"]) + ", " + str(item["healthy_people"]) + " (" + str(percentPeople(item["healthy_people"])) + "%) healthy people.")
        list_death.append(item["deaths"])
        hover_death.append("Day " + str(item["day"]) + ", " + str(item["deaths"]) +  " (" + str(percentPeople(item["deaths"])) + "%) dead people.")
        list_sick.append(item["sick"])
        hover_sick.append("Day " + str(item["day"]) + ", " + str(item["sick"]) + " (" + str(percentPeople(item["sick"])) + "%) sick people.")
    
    from plotly.offline import plot
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list_days,
        y=list_death,
        hovertext = hover_death,
        name="Dead people",
        marker_color = 'rgb(0, 0, 0)'
    ))
    fig.add_trace(go.Bar(
        x=list_days,
        y=list_sick,
        hovertext = hover_sick,
        name="Sick people",
        marker_color = 'rgb(255, 0, 0)'
    ))
    fig.add_trace(go.Bar(
        x=list_days,
        y=list_people,
        hovertext = hover_people,
        name="Healthy people",
        marker_color = 'rgb(180, 180, 180)'
    ))
    temp_string = "Epidemic evolution with " + str(const.nb_of_people) + " people." 
    fig.update_layout(barmode='stack', title_text=temp_string)
    # fig.show work only with Jupyter Notebook
    # (Verified working with the "Python Interactive Window" of VSCode)
    #fig.show()
    # Display in you default browser
    plot(fig)


# ------------------------------ STARTUP --------------------------------------


# Start simpy environnement
env = simpy.Environment()
start_time = time.time()

# Startup the log file
try:
    os.remove("individualActions.log")
except:
    print("Error, cannot delete file")
if (const.log_level.upper() == "DEBUG"):
    log_lvl = logging.DEBUG
elif (const.log_level.upper() == "INFO"):
    log_lvl = logging.INFO
else:
    log_lvl = logging.WARNING
logging.basicConfig(filename='individualActions.log', filemode='w',
                    format='%(levelname)s:%(message)s', level=log_lvl)

# Create the people (as in create the world and the individuals)
people = People(env)
people.graph_array = []
writeArray(people.people, "warn")

# Let the program turn for "tempValue_lenExp" (false) hours
temp_time = start_time
tempValue_lenExp = const.lenght_experiment * 24 + 1
env.run(until=tempValue_lenExp)
print("Elapsed total time : %s" %
      str(timedelta(seconds=(time.time() - start_time))))
logText("Elapsed total time : %s" %
        str(timedelta(seconds=(time.time() - start_time))), "info")
logging.shutdown()
print_graph(people.graph_array)