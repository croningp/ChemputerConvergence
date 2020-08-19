from os import path

import ChemputerAPI
import SerialLabware
import sys

from chempiler import Chempiler

# let the user change this to experiment name
experiment_name = input("What is the code of your current experiment? ")

root = path.abspath(path.curdir)
output_dir = path.join(root, 'logs')
graphml_file = path.join(root, "MIDA_20_v07.json")
c = Chempiler(experiment_name, graphml_file, output_dir,
                      simulation=False, device_modules=[ChemputerAPI, SerialLabware])

# start video recording
c.start_recording(0)
c.camera.change_recording_speed(2000)

####################
# Global constants #
####################

# pumping speeds
default_speed_very_slow = 5  # mL/min
default_speed_slow = 10  # mL/min
default_speed = 20 # mL/min
default_speed_fast = 50  # mL/min
default_speed_very_fast = 100  # mL/min
room_temperature = 30

####################
# Global Funxtions #
####################

def clean_separator():
    c.move("flask_water", "flask_separator", 75, speed=default_speed_very_fast, dest_port="top")
    c.stirrer.set_stir_rate("flask_separator", 700)
    c.stirrer.stir("flask_separator")
    c.wait(180)
    c.stirrer.stop_stir("flask_separator")
    c.move("flask_separator", "waste_6", 75, speed=default_speed_very_fast, src_port="bottom")
    c.move("flask_isopropanol", "flask_separator", 25, speed=default_speed_very_fast, dest_port="top")
    c.move("flask_separator", "waste_6", 25, speed=default_speed_very_fast, src_port="bottom")

def deoxygenate_flask(obj, time):
    if obj == "flask_holding":
        pos = 1
    elif obj == "reactor_1":
        pos = 3
    elif obj == "reactor_2":
        pos = 4
    else:
        raise ValueError('Unexpected flask.')

    for _ in range(5):
        c["schlenk_line"].switch_vacuum(pos)
        c.wait(time)
        c["schlenk_line"].switch_argon(pos, pressure="low")
        c.wait(time)
        
def preclean_reactor(reactor_id):
    for _ in range(2):
        c.move("flask_THF", reactor_id, 20, speed=default_speed_fast, dest_port="1")
        c.move(reactor_id, "waste_4", 25, speed=default_speed_fast, src_port="0")

def clean_rotavap():
    c['rotavap'].lift_down()
    c.move("flask_isopropanol", "rotavap", 20, speed=default_speed_very_fast)
    c['rotavap'].rotation_speed_sp = 180
    c['rotavap'].start_rotation()
    c.wait(60)
    c['rotavap'].stop_rotation()
    c.move("rotavap", "waste_5", 25, speed=default_speed_fast)

    for _ in range(2):
        c.move("eluent_b", "rotavap", 25, speed=default_speed_very_fast)
        c['rotavap'].rotation_speed_sp = 180
        c['rotavap'].start_rotation()
        c.wait(60)
        c['rotavap'].stop_rotation()
        c.move("rotavap", "waste_5", 25, speed=default_speed_fast)
        
    c.move("rotavap", "waste_5", 25, speed=default_speed_fast)
    c['rotavap'].lift_up()
    # dry it with vacuum
    c.vacuum.set_vacuum_set_point("rotavap", 10)
    c.vacuum.start_vacuum("rotavap")
    c.wait(300)
    c.vacuum.stop_vacuum("rotavap")
    c.vacuum.vent_vacuum("rotavap")

def clean_rotavap_with_THF():
    #ensure that the walls of the flask are cleaned properly
    c['rotavap'].temperature_sp = 60
    c['rotavap'].start_heater()
    c['rotavap'].lift_down()
    c.move("eluent_b", "rotavap", 100, speed=default_speed_fast)
    c.wait(180)
    c.move("rotavap", "waste_5", 120, speed=default_speed_slow)
    c.vacuum.start_vacuum("rotavap")
    c.wait(180)
    c.vacuum.stop_vacuum("rotavap")
    c['rotavap'].stop_heater()
    c['rotavap'].lift_up()
    c.vacuum.vent_vacuum("rotavap")
    c['rotavap'].temperature_sp = 40
    

def rotavap_evaporate(temp_heater=50, temp_chiller=4, t_1=300, t_2=900, t_3=300):
    c.chiller.set_temp("rotavap", temp_chiller)
    c.chiller.start_chiller("rotavap")
    c['rotavap'].temperature_sp = temp_heater
    c['rotavap'].start_heater()
    c['rotavap'].lift_down()
    c['rotavap'].rotation_speed_sp = 100
    c['rotavap'].start_rotation()
    c.move("rotavap", "waste_2", volume=25, src_port="collect", speed=default_speed_slow)
    c.vacuum.set_vacuum_set_point("rotavap", 300)
    c.vacuum.start_vacuum("rotavap")
    c.wait(t_1)
    c.vacuum.stop_vacuum("rotavap")
    c['vacuum_pump'].vent(vent_status=1)
    c.move("rotavap", "waste_2", volume=125, src_port="collect", speed=default_speed_very_fast)
    c.move("argon", "waste_5", volume=10, speed=default_speed_very_fast)  # empty tubing
    c.move("argon", "rotavap", volume=50, speed=default_speed_very_fast)  # empty tubing
    c.vacuum.set_vacuum_set_point("rotavap", 100)
    c['vacuum_pump'].vent(vent_status=0)
    c.vacuum.start_vacuum("rotavap")
    c.wait(t_2)
    c.vacuum.stop_vacuum("rotavap")
    c['vacuum_pump'].vent(vent_status=1)
    c.move("rotavap", "waste_2", volume=125, src_port="collect", speed=default_speed_very_fast)
    c.move("argon", "waste_5", volume=10, speed=default_speed_very_fast)  # empty tubing
    c.move("argon", "rotavap", volume=50, speed=default_speed_very_fast)  # empty tubing
    c.vacuum.set_vacuum_set_point("rotavap", 10)
    c['vacuum_pump'].vent(vent_status=0)
    c.vacuum.start_vacuum("rotavap")
    c.wait(t_3)
    c['rotavap'].stop_rotation()
    c.vacuum.stop_vacuum("rotavap")
    c['rotavap'].lift_up()
    c.chiller.stop_chiller("rotavap")
    c['vacuum_pump'].vent(vent_status=1)
    c['rotavap'].stop_heater()
    c.move("rotavap", "waste_2", volume=50, src_port="collect", speed=default_speed_very_fast)
    c.move("argon", "waste_5", volume=10, speed=default_speed_very_fast) 
    c.move("argon", "rotavap", volume=50, speed=default_speed_very_fast) 
    c['vacuum_pump'].vent(vent_status=0)
    

def deoxygenate_rotavap():
    for _ in range(4):
        c['vacuum_pump'].vent(vent_status=0)
        c.vacuum.set_vacuum_set_point("rotavap", 10)
        c.vacuum.start_vacuum("rotavap")
        c.wait(60)
        c.vacuum.stop_vacuum("rotavap")
        c.vacuum.vent_vacuum("rotavap")
        c['vacuum_pump'].vent(vent_status=1)
        c.wait(120)


def deoxygenate_backbone():
        c.move("argon", "waste_7", 250, speed=default_speed_very_fast)

def clean_flask(obj):
    for _ in range(2):  
        c.move("flask_water", obj, 5, speed=default_speed_very_fast)
        c.move(obj, "waste_3", 25, speed=default_speed_very_fast)
        c.move("flask_isopropanol", obj, 10, speed=default_speed_very_fast)
        c.move(obj, "waste_3", 25, speed=default_speed_very_fast)
        c.move("flask_ether", obj, 12, speed=default_speed_very_fast)
        c.move(obj, "waste_3", 25, speed=default_speed_very_fast)
    c.move("flask_ether", obj, 15, speed=default_speed_very_fast)
    c.move(obj, "waste_3", 25, speed=default_speed_very_fast)

def clean_backbone(): 
    #Clean back bone to avoid salt precipitation
    c.move("flask_water", "waste_6", 10, speed=default_speed_very_fast)
    c.move("flask_isopropanol", "waste_7", 10, speed=default_speed_very_fast)
    c.move("flask_ether", "waste_7", 10, speed=default_speed_very_fast)
    c.move("flask_THF", "waste_7", 10, speed=default_speed_very_fast)
    c.move("flask_THF", "waste_7", 10, speed=default_speed_very_fast)

def clean_backbone_with_THF(): 
    #Clean back bone
    c.move("flask_THF", "waste_7", 10, speed=default_speed_very_fast)
    c.move("flask_THF", "waste_7", 10, speed=default_speed_very_fast)
    c.move("flask_THF", "waste_7", 10, speed=default_speed_very_fast)

def deprotection(vol_NaOH, vol_buffer, vol_Et2O, vol_NaCl, cartridge_ID):
    # The deprotection takes place in the separator funnel
    #Start stirring
    c.stirrer.set_stir_rate("flask_separator", 500)
    c.stirrer.stir("flask_separator")
    # Add solution of sodium hydroxide (24 mmol, 960mg) in 24 mL of water slowly
    c.move("flask_NaOH", "flask_separator", vol_NaOH, initial_pump_speed=default_speed_fast,
           mid_pump_speed=default_speed_fast, end_pump_speed=5, dest_port="bottom")
    # Do the deprotection for 20 min by stirring
    c.wait(1800)
    # Add phoshate buffer (pH = 6, 0.5 M) and diethyl ether and stir
    c.move("flask_phosphate_buffer", "waste_6", 5, speed=default_speed_fast)
    c.move("flask_phosphate_buffer", "flask_separator", vol_buffer, speed=default_speed_fast, dest_port="bottom")
    # Add brine to improve phase separation
    c.move("flask_NaCl", "flask_separator", 5, speed=default_speed_fast, dest_port="bottom")
    # Wash line with water
    c.move("flask_water", "waste_6", 5, speed=default_speed_fast)
    # Add diethyl ether
    c.move("flask_ether", "flask_separator", vol_Et2O, speed=default_speed_fast, dest_port="top")

    # Stirr for few seconds and allow reaction mixture to separate
    c.wait(60)
    c.stirrer.stop_stir("flask_separator")
    c.stirrer.set_stir_rate("flask_separator", 100)
    c.stirrer.stir("flask_separator")
    c.wait(60)
    c.stirrer.stop_stir("flask_separator")
    c.wait(60)

    # Remove the aqueous phase and add sat. sodium chloride
    c.move("flask_separator", "waste_6", 10, speed=default_speed_slow)
    c.pump.separate_phases("flask_separator", "waste_6", "flask_separator")
    c.move("flask_NaCl", "flask_separator", vol_NaCl, speed=default_speed_fast, dest_port="top")
    c.move("flask_water", "waste_6", 5, speed=default_speed_fast)

    # Stirr for one minute and allow reaction mixture to separate
    c.stirrer.set_stir_rate("flask_separator", 500)
    c.stirrer.stir("flask_separator")
    c.wait(60)
    c.stirrer.stop_stir("flask_separator")
    c.stirrer.set_stir_rate("flask_separator", 100)
    c.stirrer.stir("flask_separator")
    c.wait(60)
    c.stirrer.stop_stir("flask_separator")
    c.wait(120)

    # Remove the aqeous phase
    c.move("flask_separator", "waste_6", 10, speed=default_speed_slow)
    c.pump.separate_phases("flask_separator", "waste_6", "flask_separator")

    # Remove the dead volume
    c.move("flask_separator", "waste_6", 2, speed=default_speed_fast)

    # to make the bacbone is dry
    clean_backbone()

    # Switch to the drying cartridge & Transfer to the rotavap to remove the solvent
    c.move("flask_separator", "rotavap", 130, speed=default_speed_slow, through_nodes=cartridge_ID)

    #Clean back bone to avoid salt precipitation
    clean_backbone()

    # rinse with THF
    c.move("eluent_b", "rotavap", 20, speed=default_speed, through_nodes=cartridge_ID)

    # Remove the solvent here
    rotavap_evaporate(temp_heater=50, temp_chiller=4, t_1=360, t_2=240, t_3=0)
    # Free boronic acid in the rotovap
    # Next: Dissolve in THF and deoxygenate


def coupling(reactor_ID, temp, addition_speed, rxn_time):
    c["schlenk_line"].switch_argon(1, pressure="low")
    c["schlenk_line"].switch_argon(3, pressure="low")
    c["schlenk_line"].switch_argon(4, pressure="low")
    c["schlenk_line"].switch_argon(6, pressure="low")

    # deoxygenate the holding flask and backbone by moving nitrogen
    c.camera.change_recording_speed(10)
    clean_backbone()
    deoxygenate_backbone()
    c.move("flask_holding", "waste_3", 25, speed=default_speed_very_fast)
    deoxygenate_flask("flask_holding", 60)
    
    # Deoxygentate rotavap
    deoxygenate_rotavap()
    
    # Dissolve boronic acid in rotavap in THF
    c.move("flask_THF", "rotavap", 20, speed=default_speed_fast)
    c['rotavap'].rotation_speed_sp = 100
    c['rotavap'].start_rotation()
    c['rotavap'].lift_down()
    c.wait(600)
    c['rotavap'].stop_rotation()
    
    # Move it to the holding flask and deoxygenate
    c.move("rotavap", "flask_holding", 25, src_port="evaporate", speed=default_speed_fast)
    c.move("flask_THF", "rotavap", 5, speed=default_speed_fast)
    c['rotavap'].start_rotation()
    c.wait(30)
    c['rotavap'].stop_rotation()
    c.move("rotavap", "flask_holding", 10, src_port="evaporate", speed=default_speed_fast)
    
    
    # deoxygenate the holding flask
    c.stirrer.set_stir_rate("flask_holding", 200)
    c.stirrer.stir("flask_holding")
    deoxygenate_flask("flask_holding", 60)
    c.stirrer.stop_stir("flask_holding")
    
    # reaction starts here
    c.stirrer.set_stir_rate(reactor_ID, 300)
    c.stirrer.stir(reactor_ID)
    deoxygenate_flask(reactor_ID, 120)
    c.stirrer.set_stir_rate(reactor_ID, 300)
    c.stirrer.stir(reactor_ID)
    clean_backbone_with_THF()
    c.move("flask_THF", reactor_ID, 28, speed=default_speed_fast)
    deoxygenate_flask(reactor_ID, 30)
    c.stirrer.set_temp(reactor_ID, temp)
    c.stirrer.heat(reactor_ID)
    c.stirrer.wait_for_temp(reactor_ID)
    c.wait(60)

    # Add boronic acid to reactor slowly over 4 hours
    c.camera.change_recording_speed(1000)
    c.move("flask_holding", reactor_ID, 20, initial_pump_speed=default_speed_slow,
           mid_pump_speed=default_speed_slow, end_pump_speed=addition_speed, dest_port="1")
    c.camera.change_recording_speed(10)
    c.move("flask_THF", "flask_holding", 10, speed=default_speed_fast)
    c.stirrer.stir("flask_holding")
    c.wait(30)
    c.stirrer.stop_stir("flask_holding")
    c.move("flask_holding", reactor_ID, volume=10, speed=50, dest_port="1")

    # wait for reaction
    c.camera.change_recording_speed(2000)
    c.wait(rxn_time)
    c.camera.change_recording_speed(5)
    c.stirrer.stop_stir(reactor_ID)
    c.stirrer.stop_heat(reactor_ID)
    c.stirrer.set_temp(reactor_ID, room_temperature)
    c.stirrer.wait_for_temp(reactor_ID)
    clean_rotavap()
    
    # Transfer rxn mixture to rotavap and evaporate
    for _ in range(3):
        c.move(reactor_ID, "rotavap", 25, speed=default_speed_slow, through_nodes="filtration_1")
        
    c.move("flask_THF", reactor_ID, 10, speed=default_speed_fast)
    c.move(reactor_ID, "rotavap", 25, speed=default_speed_slow, through_nodes="filtration_1")
    c.move("flask_THF", reactor_ID, 10, speed=default_speed_fast)
    c.move(reactor_ID, "rotavap", 25, speed=default_speed_slow, through_nodes="filtration_1")
    rotavap_evaporate(t_1=600, t_2=600, t_3=300)

def purification(column_ID, vol=24, aliq=3, time=1800):
    # redissolve in THF
    c.move("eluent_b", "rotavap", vol, speed=default_speed_fast)
    c['rotavap'].temperature_sp = 40
    c['rotavap'].start_heater()
    c['rotavap'].lift_down()
    c['rotavap'].rotation_speed_sp = 100
    c['rotavap'].start_rotation()
    c.camera.change_recording_speed(1000)
    c.wait(600)
    c.camera.change_recording_speed(10)
    c['rotavap'].stop_rotation()
    c['rotavap'].stop_heater()

    #c.breakpoint()
    c.camera.change_recording_speed(1000)

    # catch_on_columnn
    c.move("rotavap", "pump_5", vol, speed=default_speed_slow, src_port="evaporate")
    for _ in range(int(vol / aliq)):
        c.move("pump_5", "waste_column", aliq, speed=default_speed_fast, through_nodes=column_ID)
        c.connect(column_ID, "valve_column_3")
        c["valve_column_3"].move_to_position(3)
        c["valve_column_1"].move_to_position(3)
        c["schlenk_line"].switch_vacuum(6)
        c.wait(time)
        c["schlenk_line"].switch_argon(6, pressure="low")
    if vol%aliq != 0:
        c.move("pump_5", "waste_column", vol%aliq, speed=default_speed_fast, through_nodes=column_ID)
        c.connect(column_ID, "valve_column_3")
        c["valve_column_3"].move_to_position(3)
        c["valve_column_1"].move_to_position(3)
        c["schlenk_line"].switch_vacuum(6)
        c.wait(time)
        c["schlenk_line"].switch_argon(6, pressure="low")

    # redissolve in THF
    c.move("eluent_b", "rotavap", 5, speed=default_speed_fast)
    c['rotavap'].lift_down()
    c['rotavap'].rotation_speed_sp = 100
    c['rotavap'].start_rotation()
    c.wait(120)
    c['rotavap'].stop_rotation()
    c['rotavap'].stop_heater()

    # catch on columnn
    c.move("rotavap", "pump_5", 10, speed=default_speed_slow)
    for _ in range(2):
        c.move("pump_5", "waste_column", 3, speed=default_speed_fast, through_nodes=column_ID)
        c.connect(column_ID, "valve_column_3")
        c["valve_column_3"].move_to_position(3)
        c["valve_column_1"].move_to_position(3)
        c["schlenk_line"].switch_vacuum(6)
        c.wait(time)
        c["schlenk_line"].switch_argon(6, pressure="low")
    c.move("pump_5", "waste_5", 4, speed=default_speed_very_fast)

    # clean rotavap
    c['rotavap'].lift_up()
    clean_rotavap()
    c.camera.change_recording_speed(10)

    # wash backbone with diethyl ether
    c.move("flask_ether", "waste_column", 10, speed=default_speed_fast)

    # dry the column
    c.connect(column_ID, "valve_column_3")
    c.connect("schlenk_line", "valve_column_3")
    c["schlenk_line"].switch_vacuum(6)
    c.wait(1800)
    c["schlenk_line"].switch_argon(6, pressure="low")

    # Remove contaminations with diethyl ether
    for _ in range(8):
        c.move("flask_ether", "waste_column", 25, initial_pump_speed=default_speed_fast,
               mid_pump_speed=default_speed_slow, end_pump_speed=default_speed_fast, through_nodes=column_ID)

    # Release the MIDA boronate with THF
    for _ in range(6):
        c.move("eluent_b", "rotavap", 25, initial_pump_speed=default_speed_fast,
               mid_pump_speed=default_speed_slow, end_pump_speed=default_speed_fast, through_nodes=column_ID)

    # evaporate
    rotavap_evaporate()

'''
 ##     ##       ##       ##   ##     ##
 ###   ###     ##  ##     ##   ###    ##
 ## # # ##    ##    ##    ##   ## #   ##
 ##  #  ##   ##      ##   ##   ##  #  ##
 ##     ##   ##########   ##   ##   # ##
 ##     ##   ##      ##   ##   ##    ###
 ##     ##   ##      ##   ##   ##     ##
'''
# Make sure everything is connected to argon
c["schlenk_line"].switch_argon(1, pressure="low")
c["schlenk_line"].switch_argon(3, pressure="low")
c["schlenk_line"].switch_argon(4, pressure="low")
c["schlenk_line"].switch_argon(6, pressure="low")


######### Deprotection ##########
c.camera.change_recording_speed(10)
# ADD MIDA boronate to the separator funnel 8 mmol
c.move("eluent_b", "flask_separator", 100, speed=default_speed_fast, dest_port="bottom")
# Dissolve the MIDA ester
c.stirrer.set_stir_rate("flask_separator", 600)
c.stirrer.stir("flask_separator")
c.wait(240)
c.stirrer.stop_stir("flask_separator")
#deprotect MIDA ester
deprotection(vol_NaOH=24, vol_buffer=24, vol_Et2O=30, vol_NaCl=24, cartridge_ID="drying_1")
clean_separator()
# c.breakpoint()

########################### Coupling #####################################
# The reactor flask is charged with bifunctional MIDA boronate 2.64 mmol #
# and XPHOS 2nd generation palladacycle(0.136 mmol, 104 mg)              #
# and K3PO4 (24 mmol, 5.096 g)                                           #
# and warned to 55 oC before being deoxygenated                          #
##########################################################################
coupling(reactor_ID="reactor_1", temp=55, addition_speed=0.083, rxn_time=4*3600)
# c.breakpoint()

########### Purification #############
purification(column_ID="column_1", vol=24, aliq=3, time=1800)
c.camera.change_recording_speed(2000)
# c.breakpoint()