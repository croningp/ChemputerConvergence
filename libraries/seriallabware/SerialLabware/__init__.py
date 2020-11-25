# coding=utf-8
# !/usr/bin/env python
"""
"__init__.py" -- SerialLabware module init file
===================================

.. module:: SerialLabware
   :platform: Windows
   :synopsis: SerialLabware module init file
   :license: BSD 3-clause
.. moduleauthor:: Sebastian Steiner <s.steiner.1@research.gla.ac.uk>

(c) 2018 The Cronin Group, University of Glasgow

This file imports all public classes so the user can use `from SerialLabware import [class]`. Always keep this list up
to date!

For style guide used see http://xkcd.com/1513/
"""

# Cronin
from .devices.Cronin.conductivity_sensor import ConductivitySensor
from .devices.Cronin.shaker_stirrer import ShakerStirrer
from .devices.Cronin.heating_pad import HeatingPad

# Heidolph
from .devices.Heidolph.MR_Hei_Connect_stirrer import MRHeiConnect
from .devices.Heidolph.RZR_2052_Control_stirrer import RZR_2052
from .devices.Heidolph.Hei_Torque_100_Control_stirrer import HeiTORQUE_100

# Huber
from .devices.Huber.Petite_Fleur_chiller import Huber

# IKA
from .devices.IKA.Microstar_75_stirrer import IKAmicrostar75
from .devices.IKA.RCT_digital_stirrer import IKARCTDigital
from .devices.IKA.RET_Control_Visc_stirrer import IKARETControlVisc
from .devices.IKA.RV10_rotavap import IKARV10

# JULABO
from .devices.JULABO.CF41_chiller import JULABOCF41

# TriContinent
from .devices.Tricontinent.C3000_pump import C3000

# Vacuubrand
from .devices.Vacuubrand.CVC_3000_vacuum import CVC3000

# Simulated devices
from .devices.sim_devices import *
