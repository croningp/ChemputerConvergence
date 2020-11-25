# coding=utf-8
# !/usr/bin/env python
"""
"pump_random_test" -- Stress test for Chemputer pumps
=====================================================

.. module:: pump_random_test
   :platform: Unix, Windows
   :synopsis: Moves a pump to random volumes at random speeds.
.. moduleauthor:: Sebastian Steiner <s.steiner.1@research.gla.ac.uk>

(c) 2018 The Cronin Group, University of Glasgow. This work is licensed under BSD 3-clause.

This test moves a pump to random absolute volumes at random speeds. It never moves the pump back to home, so positioning
inaccuracies will add up and become apparent. The duration of the moves is estimated so the user can work out if a slow
move is still ongoing, or if something has gone tits up.

For style guide used see http://xkcd.com/1513/
"""

from ChemputerAPI.Chemputer_Device_API import initialise_udp_keepalive, ChemputerPump
import logging
from random import randint
from time import sleep
import os
import inspect

""" CONSTANTS """
ip_ending = 44

# start UDP keepalive and instantiate pump
initialise_udp_keepalive(("192.168.255.255", 3000))
sleep(0.1)
p = ChemputerPump(address="192.168.1.{0}".format(ip_ending), name="test")

# set up logging
HERE = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
fh = logging.FileHandler(filename=os.path.join(HERE, "log_files", "pump_{0}_test.txt".format(ip_ending)))
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s ; %(message)s")
fh.setFormatter(formatter)
p.logger.addHandler(fh)

# make pump ready
p.read_errors()
p.clear_errors()
p.read_errors()
sleep(0.1)
p.move_to_home(50)
p.wait_until_ready()

# initialise variables
old_pos = 0
old_speed = 0
no_of_moves = 0

# run until further notice
while True:
    while True:  # work out new target volume
        new_pos = randint(0.5, 10)

        # check if new volume is more than half a millilitre away from the old volume to avoid infinitesimal moves
        if new_pos != old_pos and ((new_pos - old_pos) < -0.5 or (new_pos - old_pos) > 0.5):
            move_volume = abs(old_pos - new_pos)
            old_pos = new_pos
            break

    while True:  # work out new speed
        new_speed = randint(0.1, 50)

        # make sure new speed is different from old speed
        if new_speed != old_speed:
            old_speed = new_speed
            break

    no_of_moves += 1
    estimated_duration = (move_volume / new_speed) * 60
    p.logger.info("Move Nr. {0}: Pump is moving to {1}uL at {2}uL/min which is going to take approx. {3:.1f} seconds".format(no_of_moves, new_pos, new_speed, estimated_duration))
    p.move_absolute(new_pos, new_speed)
    p.wait_until_ready()
