# coding=utf-8
# !/usr/bin/env python
"""
"usage_example" -- Usage example for the Chemputer API
============================================================

.. module:: usage_example
   :platform: Unix, Windows
   :synopsis: Take several pumps and valves through some basic motions
.. moduleauthor:: Sebastian Steiner <s.steiner.1@research.gla.ac.uk>

(c) 2018 The Cronin Group, University of Glasgow. This work is licensed under BSD 3-clause.

This example shows how to instantiate the devices, make them ready for use, and then have them perform some basic moves.

For style guide used see http://xkcd.com/1513/
"""

from ChemputerAPI import ChemputerPump, ChemputerValve

# unless your script implements a logger of its own, you may want to configure and enable logging to read the API's
# messages and replies. This can also be accomplished by uncommenting this statement in line 54 in the API.
import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s ; %(levelname)s ; %(message)s")

# Then, instantiate your devices. Check the IP addresses are correct, and give the devices descriptive names.
solvent_pump = ChemputerPump("192.168.1.10", "Solvent pump")
solvent_valve = ChemputerValve("192.168.1.20", "Solvent valve")
reagent_pump = ChemputerPump("192.168.1.11", "Reagent pump")
reagent_valve = ChemputerValve("192.168.1.21", "Reagent valve")

# After startup, some error flags are set. By default those are Watchdog error and Shutdown error, which is to be
# expected. If the device was freshly programmed, it will also display a Configuration error. In that case, refer to
# the pump_config.py and valve_config.py examples. In order to make the devices operational, the errors need to
# be cleared:
solvent_pump.clear_errors()
solvent_pump.wait_until_ready()  # wait for a positive reply
solvent_valve.clear_errors()
solvent_valve.wait_until_ready()
reagent_pump.clear_errors()
reagent_pump.wait_until_ready()
reagent_valve.clear_errors()
reagent_valve.wait_until_ready()

# The first move for any device has to be a move to home. For the valves, that's straightforward:
solvent_valve.move_home()
solvent_valve.wait_until_ready()
reagent_valve.move_home()
reagent_valve.wait_until_ready()

# For pumps, two distinct commands are available, move_to_home() and hard_home(). move_to_home() uses the previously
# stored home position and returns to it. hard_home() moves the carriage down until it stalls, then backs up a
# predefined number of steps, and records this position as new home. Since readings may sometimes drift, it is
# recommended to use hard_home() for the very first homing, though it is not mandatory. Both homing commands take one
# argument, which is the moving speed in mL/min. This has to be decided based on syringe size and application. 50mL/min
# is a good opening gambit, but a sensible value should be determined experimentally!
solvent_pump.move_to_home(50)
solvent_pump.wait_until_ready()
reagent_pump.hard_home(50)
reagent_pump.wait_until_ready()

# Now the devices are ready for use. They can be moved sequentially like so:
solvent_pump.move_absolute(20, 50)  # move to 20mL at 50mL/min
solvent_pump.wait_until_ready()
solvent_valve.move_to_position(3)  # positions are numbered 0-5!
solvent_valve.wait_until_ready()

# Or multiple devices can be moved at once, and then collectively waited on, like so:
solvent_valve.move_to_position(2)
reagent_valve.move_to_position(5)
solvent_valve.wait_until_ready()
reagent_valve.wait_until_ready()

# Illegal moves will raise errors:
solvent_pump.move_absolute(-10, 50)  # this will raise an error because there is no negative absolute volume

solvent_pump.move_to_home(50)
solvent_pump.wait_until_ready()
solvent_pump.move_relative(-1, 50)  # this will equally raise an error because the pump first moves to 0, and then
                                    # tries to dispense even more, which isn't possible

solvent_pump.move_absolute(10, 50)
solvent_pump.wait_until_ready()
solvent_pump.move_relative(-1, 50)  # this, however, would work, with the pump ending at 9mL volume

solvent_valve.move_to_position(6)  # this move is out of range, as the ports of the six-way valve are numbered 0-5!

# Sending two successive commands to the same device without waiting for a command to be complete will raise an error:
solvent_pump.move_absolute(10, 50)
solvent_pump.move_to_home(50)  # this line will raise an error since the device is still in motion
