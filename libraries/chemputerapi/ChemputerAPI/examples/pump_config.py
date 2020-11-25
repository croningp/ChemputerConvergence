# coding=utf-8
# !/usr/bin/env python
"""
"pump_config" -- Initial configuration of Chemputer pumps
============================================================

.. module:: pump_config
   :platform: Unix, Windows
   :synopsis: Configure a newly programmed pump and make it ready for use.
.. moduleauthor:: Sebastian Steiner <s.steiner.1@research.gla.ac.uk>

(c) 2018 The Cronin Group, University of Glasgow. This work is licensed under BSD 3-clause.

This example shows how to configure a Chemputer pump after programming it. This process may be done in an automated
fashion by running this script, or by sending the commands one by one from the command line.

For style guide used see http://xkcd.com/1513/
"""

from ChemputerAPI import ChemputerPump

# Unless your script implements a logger of its own, you may want to configure and enable logging to read the API's
# messages and replies. This can also be accomplished by uncommenting this statement in line 54 in the API.
import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s ; %(levelname)s ; %(message)s")

# Then, instantiate your device. By default, after programming the device will have the IP ending 99.
pump = ChemputerPump("192.168.1.99")

# The pump requires some pieces of information to function correctly. Most of them are inconsequential to the mere user,
# except for the syringe size used. Thus, the first thing to do is to write a default configuration to the device:
pump.write_default_pump_configuration(syringe_size=25)

# The pump should reply the values, followed by a confirmation that the config write was successful.
# Next, errors are cleared:
pump.clear_errors()

# It is advisable to check if the device is now free of errors:
pump.read_errors()

# Next, the home position should be determined. This is done by calling hard_home()
pump.hard_home(50)

# The pump will stall itself against the base, back up a few steps, and reply with the home reading. A reading between
# 700 and 900 is ok, if the reading is higher, check the Hall effect sensor and/or the magnet. If it reports a failure,
# the reason is mostly a faulty sensor, or a magnet mounted the wrong way around.

# Now the pump is ready for use. It is recommended to have it make a few moves and check if everything works:
pump.move_absolute(10, 50)  # check if the volume is actually 10mL
pump.wait_until_ready()
pump.move_relative(1, 50)
pump.wait_until_ready()
pump.move_relative(-2, 50)  # check if it moves back to 9mL again
pump.wait_until_ready()
pump.move_to_home(50)  # check if it returns to the proper home position
pump.wait_until_ready()

# Lastly, a new IP address is assigned:
pump.assign_ip_address("192.168.1.11")

# At this point the script will hang until the TCP connection times out, but it matters not. The configuration is done
# and the device is ready for use.
