# coding=utf-8
# !/usr/bin/env python
"""
"valve_random_test" -- Stress test for Chemputer valves
=======================================================

.. module:: valve_random_test
   :platform: Unix, Windows
   :synopsis: Moves a valve to random positions.
.. moduleauthor:: Sebastian Steiner <s.steiner.1@research.gla.ac.uk>

(c) 2018 The Cronin Group, University of Glasgow. This work is licensed under BSD 3-clause.

This test moves a valve to random positions and records the move duration. Legible messages are logged to the console,
while the raw data is logged to a file and can be processed with Excel or Origin. The main purpose is to spot if
positions are missed or skipped.

For style guide used see http://xkcd.com/1513/
"""

from ChemputerAPI.Chemputer_Device_API import initialise_udp_keepalive, ChemputerValve
import logging
from random import randint
import time
import os
import inspect

""" CONSTANTS """
ip_ending = 44

########################################################################################################################
#   logging                                                                                                            #
########################################################################################################################

# create main thread logger
logger = logging.getLogger("main_logger")
logger.setLevel(5)


# create new level for values
class ValueFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == 5


# create filter instance
file_filter = ValueFilter()

# create file handler which logs all messages
HERE = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
fh = logging.FileHandler(filename=os.path.join(HERE, "log_files", "valve_{0}_test.txt".format(ip_ending)))
fh.setLevel(5)
fh.addFilter(file_filter)

# create console handler which logs all messages
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter and add it to the handlers
file_formatter = logging.Formatter("%(message)s")
fh.setFormatter(file_formatter)
console_formatter = logging.Formatter("%(asctime)s ; %(module)s ; %(message)s")
ch.setFormatter(console_formatter)

# add the handlers to the loggers
logger.addHandler(fh)
logger.addHandler(ch)

# create file header
logger.log(level=5, msg="Move Nr; Old Pos; New Pos; Nr of Pos; Move Duration")

########################################################################################################################
#   setup                                                                                                              #
########################################################################################################################

# start UDP keepalive broadcast
initialise_udp_keepalive(("192.168.255.255", 3000))
time.sleep(0.5)

# instantiate valve
v = ChemputerValve("192.168.1.{0}".format(ip_ending), "Leeroy Jenkins")
time.sleep(0.5)

v.clear_errors()
time.sleep(0.1)
v.move_home()
v.wait_until_ready()

########################################################################################################################
#   testing                                                                                                            #
########################################################################################################################

old_pos = 0
no_of_moves = 0

while True:
    # work out next position
    while True:
        new_pos = randint(0, 5)
        if new_pos != old_pos:
            break
    no_of_moves += 1
    logger.info("Move Nr. {0}: Valve is moving to position {1}".format(no_of_moves, new_pos))

    # work out distance
    positive_move = old_pos - new_pos
    negative_move = new_pos - old_pos

    if positive_move < 0:
        positive_move += 6
    if negative_move < 0:
        negative_move += 6

    if positive_move < negative_move:
        number_of_positions = positive_move
    elif positive_move > negative_move:
        number_of_positions = negative_move
    else:
        number_of_positions = positive_move  # if they are equal it doesn't matter

    # start measuring time
    time_before = time.time()

    # move to position
    v.move_to_position(new_pos)
    v.wait_until_ready()

    # record duration
    time_after = time.time()
    duration = time_after-time_before

    logger.log(level=5, msg="{0}; {1}; {2}; {3}; {4}".format(no_of_moves, old_pos, new_pos, number_of_positions, duration))

    # update position
    old_pos = new_pos

    time.sleep(0.1)
