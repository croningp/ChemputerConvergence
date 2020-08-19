from chempiler import Chempiler
import ChemputerAPI
import SerialLabware

c = Chempiler("labbook_code", "diazirine-graph.json",
              "output_folder", simulation=False, device_modules=[ChemputerAPI, SerialLabware])

# c.breakpoint()
dead_volume_filter = 10

volume_levulinic_acid = 9.31  # mL, 7.5 g in 7.31 mL (64.588 mmol, 8.83 M)
volume_ammonia_MeOH = 80  # mL, for a 7M solution (Alfa-Aesar, 700 mmol)
volume_HOSA = 10.0  # mL, 1.5 M in MeOH, so 8.39 g in 49.5 mL (49.5 / 5) or 11.0 in 60 mL in this case
volume_MeOH_washing = 10  # mL
volume_water_rv = 40  # mL
volume_DMEA = 5.6  # mL (now 130 + 10 mmols excess?) 15.16 or 7.6 if KOH (4.60 g, 82 mmols) is already present in the reactor.
volume_Iodine = 110  # mL 16.5 g (65.01 mmol) of iodine in 100 mL of MeOH
volume_Diethylether_dilution = 40  # mL
volume_sodium_sulfite = 15  # mL, 15 w% in water (basically 12 mmols every 10 mL)
volume_HCl = 32 # mL, 3 M (65.105 mL of 35% HCl diluted up to 250 mL) (32 mL is equivalent to 96.0 mmols)

###################################
# Column Chromatography constants #
###################################

flask_eluent = "flask_DCM"
elution_speed = 50  # mL/min
priming_speed = 50  # mL/min
eluent_aspiration_speed = 50  # mL/min
priming_volume = 550  # mL
dead_fraction_volume = 10  # mL, yet to be determined, for volume determination
collect_fraction_volume = 330  # mL
volume_loading = 10  # mL

### this needs to actually be checked, now default for one g of product
#############################
# Estherification constants #
#############################

volume_DCM = 30 #mL 10 ml per g of diazirine
volume_NHS_in_ACN = 25.0 #ml 3.3M NHS in Acetonitrile (5.66g in 14.9 mL)
volume_EDCI_in_DCM = 140 #ml 0.5 M (11.4995g in 120 mL) MW: 155.25

# Conditions for precipitation has to be determined each time there's a change,
# Suggested: a 50/50 %mol of Methanol/diethylether to form 1M concentration with the product and cooling to -20 °C
volume_diethyl_ether_precipitation = 14.33 # mL Grams of Et2O:  10.22 g  and volume:  14.33 mL
volume_MeOH_precipitation = 29.85 #  Grams of MeOH:  23.64 g  and volume:  29.85 mL
volume_brine = 40 #mL

###########################
# Environmental Constants #
###########################
ice_bath = -3 # in °C
cold_bath = -16 # in ° C
crist_bath = -20 # in ° C
rv_temp_one = 27 # in °C

default_speed_viscous = 3 # mL/min
default_speed_slow = 20  # mL/min
default_speed_fast = 60  # mL/min
default_speed_dead_slow = 2.5  # mL/min

default_speed_rv = 180 # RPM,  rotation speed of rotavap
stirring_rate_diazirine = 500 #RPM, reactor_reactor magnetic stirrer speed
extraction_overhead_stirring_rate = 800  # RPM
extraction_settling_stirring_rate = 30  # RPM

# ===================
# ===FUNCTIONS===================================================================================================
#====================
def evaporate_to_dryness(distillate_volume_one, distillate_volume_two, distillate_volume_three, pre_vacuum, dist_vacuum , end_vacuum, degas_time, distillation_time, drying_time, rv_temperature):
    # INSRUCTIONS # volume to distillate, degas pressure, distillation vacuum, drying vacuum, time degas, time distillation, time drying
    # lower flask, start rotation
    c.camera.change_recording_speed(5)
    c['rotavap'].set_interval = 0
    # c.connect('carousel_top', 'carousel_bottom', src_port='route', dest_port='route')
    c['rotavap'].lift_down()
    c['rotavap'].rotation_speed_sp = default_speed_rv
    c['rotavap'].start_rotation()

    # degas
    c.camera.change_recording_speed(100)
    c.vacuum.set_vacuum_set_point('rotavap', pre_vacuum)
    c.vacuum.start_vacuum('rotavap')
    c['rotavap'].temperature_sp = rv_temperature
    c['rotavap'].start_heater()
    c.wait(degas_time)

    # vent and empty
    c.camera.change_recording_speed(300)
    c['rotavap'].lift_up()
    c['rotavap'].stop_rotation()
    c.wait(10)
    c.vacuum.stop_vacuum('rotavap')
    c.vacuum.vent_vacuum('rotavap')
    c.camera.change_recording_speed(200)
    c.move('rotavap', 'waste_rotary', distillate_volume_one, speed=50, src_port='collect')

    # main distillation
    c.camera.change_recording_speed(500)
    c.vacuum.set_vacuum_set_point('rotavap', dist_vacuum)
    c.vacuum.start_vacuum('rotavap')
    c['rotavap'].lift_down()
    c['rotavap'].start_rotation()
    c.wait(distillation_time)

    # vent and empty
    c.camera.change_recording_speed(300)
    c['rotavap'].lift_up()
    c['rotavap'].stop_rotation()
    c.wait(10)
    c.vacuum.stop_vacuum('rotavap')
    c.vacuum.vent_vacuum('rotavap')
    c.camera.change_recording_speed(200)
    c.move('rotavap', 'waste_rotary', distillate_volume_two, speed=50, src_port='collect') # TODO don't hard-code outlets

    # dry at max. vacuum
    c.camera.change_recording_speed(5)
    c['rotavap'].lift_down()
    c['rotavap'].start_rotation()
    c.vacuum.set_vacuum_set_point('rotavap', end_vacuum)
    c.camera.change_recording_speed(270)
    c.vacuum.start_vacuum('rotavap')
    c.wait(drying_time)

    # recover flask and vent
    c.camera.change_recording_speed(50)
    c['rotavap'].lift_up()
    c.wait(10)
    c['rotavap'].stop_rotation()
    c.vacuum.stop_vacuum('rotavap')
    c.vacuum.vent_vacuum('rotavap')
    c['rotavap'].stop_heater()
    c.camera.change_recording_speed(150)
    c.move('rotavap', 'waste_rotary', distillate_volume_three, speed=50, src_port='collect')

# ==========================================================
def clean_reactor(solvent_flsk, quantity):
    c.move(solvent_flsk, 'reactor_reactor', quantity, speed=60)
    c.stirrer.set_stir_rate('reactor_reactor', 400)
    c.stirrer.stir('reactor_reactor')
    c.wait(60)
    c.stirrer.stop_stir('reactor_reactor')
    c.move('reactor_reactor', 'waste_reactor', (quantity + 20), speed=70)

# =========================================================
def clean_filter(flask_washing_liquid, clean_temp): #function takes one argument, for example 'flask_ether', and washes with specified liquid
    c.camera.change_recording_speed(5)
    c.chiller.set_temp('filter_filter_top', clean_temp)
    c.chiller.start_chiller('filter_filter_top')
    c['valve_filter'].move_home()
    c.stirrer.set_stir_rate('filter_filter_top', stirring_rate_diazirine)
    c.stirrer.stir('filter_filter_top')
    c.camera.change_recording_speed(300)
    c.move(flask_washing_liquid, 'filter_filter_top', 180, speed=default_speed_fast, dest_port='top')
    c.chiller.wait_for_temp('filter_filter_top')
    c.wait(600)
    c.camera.change_recording_speed(300)
    c.stirrer.set_stir_rate('filter_filter_top', 100)
    c.move('filter_filter_top', 'waste_separator' , 200, speed=default_speed_slow)
    c.stirrer.stop_stir('filter_filter_top')
    c.chiller.set_temp('filter_filter_top', 25)
    c.connect('filter_filter_top', 'vac_filter')
    c.wait(300)
    c.connect('filter_filter_top', 'pump_separator')
    c.chiller.stop_chiller('filter_filter_top')
    c.camera.change_recording_speed(150)


# ==================================================
def clean_hose(volume_washing_hose):
    # general cleaning method for hoses and pumps. Takes the desired volume of washing liquid as an argument.
    # The cleaning agents are moved from one side through the whole backbone and pumps. By that technique, everything in between is cleaned.
    # The first cleaning step is with ether, to get rid of really reactive chemicals like chlorosulphonic acid.
    # Then everything is washed with water, followed by acetone and once again, ether, to get rid of reactive solvents.
    # make sure washing liquids are on the valve on other side of rig than waste
    # DOES NOT CLEAN ROTARY VALVE!!!

    c.camera.change_recording_speed(180)

    c.move('flask_MeOH_dry', 'waste_rotary', volume_washing_hose, speed=default_speed_fast)
    c.move('flask_ether', 'waste_reagents_1', 2, speed=default_speed_fast)
    c.move('flask_ether', 'waste_reagents_2', 2, speed=default_speed_fast)
    c.move('flask_ether', 'waste_solvents', 2, speed=default_speed_fast)
    c.move('flask_ether', 'waste_reactor', 2, speed=default_speed_fast)

    c.move('flask_ether', 'waste_separator', 5, speed=default_speed_fast)
    c.move('flask_water', 'waste_separator', volume_washing_hose, speed=default_speed_fast)
    c.move('flask_MeOH_dry', 'waste_separator', volume_washing_hose, speed=default_speed_fast)

    c.move('flask_MeOH_dry', 'waste_reactor', volume_washing_hose, speed=default_speed_fast)
    c.move('flask_MeOH_dry', 'waste_separator', volume_washing_hose, speed=default_speed_fast)
    c.move('flask_Ar_R', 'waste_reagents_1', 40, speed=50) #dries backbone a bit

    c.move('flask_ether', 'waste_separator', volume_washing_hose, speed=default_speed_fast)
    c.move('flask_ether', 'waste_separator', volume_washing_hose, speed=default_speed_fast)
    c.move('flask_Ar_R', 'waste_reagents_1', 40, speed=50) #dries backbone a bit
    c.camera.change_recording_speed(50)


# =====================================================
def reduced_clean(volume_washing):

    c.camera.change_recording_speed(180)
    c.move('flask_MeOH_dry', 'waste_rotary', volume_washing, speed=default_speed_fast)
    c.move('flask_ether', 'waste_reagents_1', 5, speed=default_speed_fast)
    c.move('flask_Ar_L', 'waste_chroma', 40, speed=50)

    c.camera.change_recording_speed(50)


# ====================================================
def clean_separator():
    c.camera.change_recording_speed(250)
    c.move('flask_ether', 'flask_separator', 100, dest_port='top', speed=50)
    c.move('flask_water', 'flask_separator', 100, dest_port='top', speed=50)
    c.stirrer.set_stir_rate('flask_separator', extraction_overhead_stirring_rate)
    c.stirrer.stir('flask_separator')
    c.wait(60)
    c.stirrer.stop_stir('flask_separator')
    c.stirrer.set_stir_rate('flask_separator', 100)
    c.stirrer.stir('flask_separator')
    c.move('flask_separator', 'waste_separator', 100, speed=50)
    c.move('flask_separator', 'waste_rotary', 100, speed=50)
    c.stirrer.stop_stir('flask_separator')


# ==============================================================================
def wash_precipitate(flask_washing_liquid, volume_washing_liquid, destination):
    #washes precipitate in filter with volume_washing_liquid of flask_washing_liquid for 2 times

    c.stirrer.set_stir_rate('filter_filter_top', 800)
    c.stirrer.stir('filter_filter_top')
    # ============================
    c.move(flask_washing_liquid, 'filter_filter_top', volume_washing_liquid, initial_pump_speed=default_speed_slow, mid_pump_speed=default_speed_fast, end_pump_speed=default_speed_slow)
    c.wait(300) #soaking for 5 min
    c.stirrer.stop_stir('filter_filter_top')
    # =============================
    c.move('filter_filter_top', destination, (1.5 * volume_washing_liquid), initial_pump_speed=default_speed_viscous, mid_pump_speed=default_speed_slow, end_pump_speed=default_speed_slow,
		   through_nodes='filtration_col')

    c.stirrer.set_stir_rate('filter_filter_top', 100)
    c.stirrer.stir('filter_filter_top')
    c.wait(30)
    c.stirrer.stop_stir('filter_filter_top')




# ======================================================================
def prime_filter(temperature, solvent_bottom, stirring_rate_prime): # sets and starts stirring and temperature(via chiller) for the flask. Additionally, puts some solvent to the bottom, so reaction solution doesnt drop through frit and crystallize beneath.
    c.camera.change_recording_speed(200)
    c.connect('filter_filter_top', 'pump_separator')

#    S SWITCH_CHILLER('filter_filter_top', 0); # No switch yet in this Rig!
    c.chiller.set_temp('filter_filter_top', temperature)
    c.chiller.start_chiller('filter_filter_top')

    c.stirrer.set_stir_rate('filter_filter_top', stirring_rate_prime)
    c.stirrer.stir('filter_filter_top')

    c.move(solvent_bottom, 'filter_filter_top', dead_volume_filter, speed=default_speed_fast, dest_port="bottom")

    c.chiller.wait_for_temp('filter_filter_top')
    c.camera.change_recording_speed(50)


# ====================================================================================================================
def transfer_from_rotavap(destination, flask_solvent, volume_solvent, aspiration_speed_solvent, temperature_heatbath):
    c.camera.change_recording_speed(36)

    #this is for cleaning
    c.camera.change_recording_speed(60)
    c.move('flask_MeOH_dry', 'waste_rotary', 3, speed=default_speed_fast)
    c.move('flask_Ar_M', 'waste_rotary', 20, speed=default_speed_fast)

    c.camera.change_recording_speed(120)
    c.move(flask_solvent, 'rotavap', volume_solvent, speed=default_speed_slow, dest_port='evaporate') # transfers solvent to rotavap to dissolve product
    c.move('flask_Ar_M', 'rotavap', 10, speed=default_speed_fast, dest_port='evaporate')

    c['rotavap'].temperature_sp = temperature_heatbath
    c['rotavap'].start_heater()
    c['rotavap'].set_interval = 60
    c['rotavap'].rotation_speed_sp = default_speed_rv
    c['rotavap'].start_rotation()
    c['rotavap'].lift_down()

    c.camera.change_recording_speed(200)
    c.wait(300) #s, let it dissolve
    c.camera.change_recording_speed(5)
    c['rotavap'].stop_rotation()
    c['rotavap'].stop_heater()
    c.camera.change_recording_speed(150)
    c.move(flask_solvent, 'waste_solvents', 3, speed=default_speed_slow)
    c.move('rotavap', destination, (volume_solvent + 10), initial_pump_speed=aspiration_speed_solvent, mid_pump_speed=default_speed_fast, end_pump_speed=default_speed_fast, src_port='evaporate')
    c.move('rotavap', destination, 20, initial_pump_speed=aspiration_speed_solvent, mid_pump_speed=default_speed_fast, end_pump_speed=default_speed_fast, src_port='evaporate')

    c.camera.change_recording_speed(60)

    c['rotavap'].lift_up()

    c.camera.change_recording_speed(160)
    c.move('flask_MeOH_dry', 'waste_rotary', 3, speed=default_speed_fast)
    c.move('flask_Ar_M', 'waste_rotary', 20, speed=default_speed_fast)

    c.camera.change_recording_speed(150)


# ===========================================================================
def rotavap_cleaning(volume_wash, rv_clean_solvent):

    c['rotavap'].set_interval = 5
    c['rotavap'].rotation_speed_sp = default_speed_rv
    c['rotavap'].start_rotation()
    c['rotavap'].lift_down()

    c.camera.change_recording_speed(160)

    # solvent cleaning
    c.move(rv_clean_solvent, 'rotavap', volume_wash, speed=default_speed_fast, dest_port='evaporate')
    c.wait(600)
    c['rotavap'].stop_rotation()
    c.move('rotavap', 'waste_rotary', (1.2 * volume_wash), speed=default_speed_fast, src_port='evaporate')
    # c.move('rotavap', 'waste_rotary', volume_wash, speed=default_speed_fast, src_port=evaporate)

    # drying out with vacuum
    c.vacuum.set_vacuum_set_point('rotavap', 3)
    c.vacuum.start_vacuum('rotavap')
    c['rotavap'].set_interval = 0
    c.wait(150)
    c.vacuum.stop_vacuum('rotavap')
    c.vacuum.vent_vacuum('rotavap')

    c['rotavap'].stop_rotation()
    c.wait(10)
    c['rotavap'].lift_up()
    c.camera.change_recording_speed(50)


# =====================================================================================================

# =======================================================================================
def separate_phases(destination_bottom_layer, destination_top_layer, volume_bottom_phase, threshold, lower_through=None, upper_through=None):
    # hand volume_organic_phase: 90% of total organic phase(will be pumped without reading)
    def discriminant(readings):
        if readings[-2] - readings[-1] > threshold:
            return True
        return False

    c.camera.change_recording_speed(24)
    c.stirrer.set_stir_rate('flask_separator', extraction_overhead_stirring_rate)
    c.stirrer.stir('flask_separator')
    c.wait(120)  # extracting
    c.stirrer.stop_stir('flask_separator')

    c.camera.change_recording_speed(60)

    c.stirrer.set_stir_rate('flask_separator', extraction_settling_stirring_rate)
    c.stirrer.stir('flask_separator')
    c.wait(200)  # settling
    c.stirrer.stop_stir('flask_separator')

    c.camera.change_recording_speed(60)

    c.move('flask_separator', destination_bottom_layer, volume_bottom_phase, speed=default_speed_slow, through_nodes=lower_through)

    c.camera.change_recording_speed(90)

    c.pump.separate_phases('flask_separator', destination_bottom_layer, destination_top_layer, discriminant=discriminant,
                           lower_phase_through=lower_through, upper_phase_through=upper_through)  # pump organic phase to rotary, dump watery layer

    c.camera.change_recording_speed(50)


# =========================================================================================================================
def anticlogging_dispense(flask_origin, destination_desired, flask_purge, volume_desired, volume_purge, dispensing_speed, route_through=None):
    # For transferring volumes that tend to clog tubes
    # def volume_dispensed = (volume_desired / div)
    for _ in range(7):
        c.move(flask_origin, destination_desired, volume_desired, initial_pump_speed=default_speed_slow, mid_pump_speed=default_speed_slow, end_pump_speed=dispensing_speed, src_port=route_through)
        c.move(flask_purge, destination_desired, volume_purge, initial_pump_speed=default_speed_slow, mid_pump_speed=default_speed_slow, end_pump_speed=default_speed_fast, src_port=route_through)




# =======================
# MAIN MAIN MAIN ========
# =============================================================================================================================
if __name__ == '__main__':
    #######################
    # Diazirine Synthesis #
    #######################
    # START
    c.start_recording(0)
    c.camera.change_recording_speed(50)
    # S PRIME(default_speed_slow); # Not needed even detrimental

    c.chiller.set_temp('filter_filter_top', -5)
    c.chiller.start_chiller('filter_filter_top')
    clean_hose(5)
    c.move('flask_MeOH_dry', 'filter_filter_top', volume_MeOH_washing, speed=default_speed_fast)
    c.move('filter_filter_top', 'waste_separator', 20, initial_pump_speed=default_speed_slow, mid_pump_speed=default_speed_fast, end_pump_speed=default_speed_fast)

    # stirring and waiting
    prime_filter(cold_bath, 'flask_MeOH_dry', stirring_rate_diazirine)

    c.camera.change_recording_speed(50)
    # charging flask
    c.move('flask_ammonia_MeOH', 'filter_filter_top', volume_ammonia_MeOH, speed=default_speed_slow)
    c.move('flask_levulinic_acid', 'waste_reactor', 2, initial_pump_speed=default_speed_viscous, mid_pump_speed=default_speed_slow, end_pump_speed=default_speed_slow)
    c.move('flask_levulinic_acid', 'filter_filter_top', volume_levulinic_acid, initial_pump_speed=default_speed_viscous, mid_pump_speed=default_speed_slow, end_pump_speed=default_speed_slow, dest_port='top')
    c.move('flask_MeOH_dry', 'filter_filter_top', 5, speed=default_speed_fast, dest_port='top')
    c.move('flask_MeOH_dry', 'waste_reagents_1', 5, speed=default_speed_fast)
    c.move('flask_Ar_L', 'waste_reactor', 20, speed=default_speed_fast)
    c.move('flask_Ar_L', 'filter_filter_top', 5, initial_pump_speed=default_speed_slow, mid_pump_speed=default_speed_fast, end_pump_speed=default_speed_fast)
    c.camera.change_recording_speed(10000)
    c.wait(10800) # 3 hours on icebath

    reduced_clean(5)

    c.camera.change_recording_speed(100)
    # add hydroxylamine-o-sulphonic acid,
    # dispense dead slow 2.5 ml/min, 4 is in how many times the adding sequence is diveded in, 2 is the volume of pure solvent to purge the tubes
    c.stirrer.set_stir_rate('flask_HOSA', 400)
    c.stirrer.stir('flask_HOSA')
    c.move('flask_MeOH_dry', 'flask_HOSA', 60, speed=default_speed_fast)
    c.wait(120)
    anticlogging_dispense('flask_HOSA', 'filter_filter_top', 'flask_MeOH_dry', volume_HOSA, 2, default_speed_dead_slow)
    c.stirrer.stop_stir('flask_HOSA')
    reduced_clean(5)
    c.camera.change_recording_speed(10000)

    c.wait(3600) # 1 h
    c.chiller.set_temp('filter_filter_top', 18) # Set temperature to 18 °C A RAMP TO ROOM TEMPERATURE otherwise
    c.wait(54000) # 15 h
    c.chiller.set_temp('filter_filter_top', 20)
    c.stirrer.stop_stir('filter_filter_top')

    # filter precipitate off
    c.camera.change_recording_speed(50)
	# Change the volume back to 250 layer
    c.move('filter_filter_top', 'rotavap', 270, initial_pump_speed=default_speed_viscous, mid_pump_speed=default_speed_slow, end_pump_speed=default_speed_slow,
		   through_nodes='filtration_col')
    wash_precipitate('flask_MeOH_dry', 80, 'rotavap')
    c.move('flask_Ar_M', 'waste_rotary', 20, speed=default_speed_fast)
    c.move('flask_Ar_M', 'rotavap', 20, initial_pump_speed=default_speed_fast, mid_pump_speed=default_speed_fast, end_pump_speed=default_speed_slow, through_nodes='filtration_col')
    c.chiller.stop_chiller('filter_filter_top')
    # c.move('flask_Ar_M', rotavap, 40, default_speed_slow, default_speed_fast, default_speed_slow)

    # clean dissolve the precipitate and move to waste done later.

    evaporate_to_dryness(1, 200, 1, 240, 135, 30, 900, 3600, 1800, rv_temp_one)
    # volume to distillate, degas pressure, distillation vacuum, drying vacuum, time degas, time distillation, time drying

    # c.breakpoint()
    # S BREAKPOINT()


    #######################
    # oxidize with iodine #
    #######################

    c.chiller.set_temp('reactor_reactor', ice_bath)
    c.chiller.start_chiller('reactor_reactor')

    # Injeecting a bit of base and cleaning the tubes
    c.move('flask_water', 'reactor_reactor', 20, speed=50)
    c.stirrer.set_stir_rate('reactor_reactor', stirring_rate_diazirine)
    c.stirrer.stir('reactor_reactor')
    c.move('flask_Ar_L', 'reactor_reactor', 10, speed=20)
    c.move('reactor_reactor', 'rotavap', 2, initial_pump_speed=default_speed_slow, mid_pump_speed=default_speed_fast, end_pump_speed=default_speed_fast)
    c.move('flask_Ar_L', 'waste_rotary', 20, speed=50)
    c.move('flask_MeOH_dry', 'waste_rotary', 5, speed=default_speed_fast)
    # ===============================================
    transfer_from_rotavap('reactor_reactor', 'flask_water', volume_water_rv, default_speed_viscous, rv_temp_one)
    #transfer_from_rotavap(reactor_reactor, 'flask_ether', 30, default_speed_slow, rv_temp_one);

    c.camera.change_recording_speed(100)
    c.chiller.wait_for_temp('reactor_reactor')
    c.stirrer.set_stir_rate('reactor_reactor', stirring_rate_diazirine)

    # c.move('flask_DMEA', 'reactor_reactor', volume_DMEA, initial_pump_speed=default_speed_slow, mid_pump_speed=default_speed_slow, end_pump_speed=default_speed_viscous) # TEA and DMEA tried without KOH but doesn't perform good
    c.move('flask_Iodine', 'reactor_reactor', volume_Iodine, initial_pump_speed=default_speed_slow, mid_pump_speed=default_speed_fast, end_pump_speed=default_speed_dead_slow) # disolve it in MeOH or EtOH instead (tried, more annoying)
    transfer_from_rotavap('reactor_reactor', 'flask_water', 20, default_speed_slow, 23)
    # Cleaning the Iodine flask to avoid contamination
    for _ in range(3):
        c.move('flask_ether', 'flask_Iodine', 18, speed=default_speed_fast)
        c.move('flask_Iodine', 'waste_reactor', 20, speed=default_speed_fast)


    # in the meantime it reacts
    c.camera.change_recording_speed(1000)
    reduced_clean(5)
    rotavap_cleaning(30, 'flask_MeOH_dry')
    rotavap_cleaning(100, 'flask_ether')
    c.camera.change_recording_speed(1000)
    c.wait(5400) # 1:30 hours:min

    # separation of phases, should be basic now, so the product should be in acqueous phase.
    # Triethylamonium ion is a phase transfer cation therefore I suppose we are trashing some product
    c.camera.change_recording_speed(50)
    c.move('flask_sodium_sulfite', 'reactor_reactor', volume_sodium_sulfite, speed=default_speed_fast)
    c.wait(1800) # 1/2 hour
    c.camera.change_recording_speed(200)
    c.stirrer.stop_stir('reactor_reactor')
    tot_volume = volume_Iodine + volume_water_rv + 80 + volume_sodium_sulfite
    c.move('reactor_reactor', 'flask_separator', tot_volume, dest_port='top', initial_pump_speed=default_speed_slow, mid_pump_speed=default_speed_fast, end_pump_speed=default_speed_fast)
    separate_phases('reactor_reactor', 'rotavap', 60, 120)

    c.stirrer.set_stir_rate('reactor_reactor', stirring_rate_diazirine)
    c.stirrer.stir('reactor_reactor')


    # c.wait(1800); Commented because unnecessary
    # S BREAKPOINT(); # LOOK AT HERE!
    c.chiller.set_temp('reactor_reactor', 5)
    # neutralise and removal of excess iodine
    c.move('flask_HCl', 'reactor_reactor', volume_HCl, speed=default_speed_slow)
    c.move('flask_ether', 'reactor_reactor', 40, speed=default_speed_fast)
    c.chiller.stop_chiller('reactor_reactor')
    # rotavap_cleaning(60, 'flask_MeOH_dry')

    # =================================================================================================================
    ##############
    # Extraction #
    ##############

    c.stirrer.stop_stir('reactor_reactor')
    c.camera.change_recording_speed(100)
    tot_volume += (volume_HCl + 40)
    c.move('reactor_reactor', 'flask_separator', tot_volume, dest_port='top', speed=default_speed_fast)
    separate_phases('reactor_reactor', 'rotavap', 80, 200, upper_through='drying_col')
    for _ in range(4):
        c.move('flask_ether', 'reactor_reactor', volume_Diethylether_dilution, speed=default_speed_fast)
        c.move('reactor_reactor', 'flask_separator', tot_volume, dest_port='top', speed=default_speed_fast)
        separate_phases('reactor_reactor', 'rotavap', 100, 200, upper_through='drying_col')

    c.camera.change_recording_speed(50)
    c.move('flask_ether', 'flask_separator', 40, dest_port='top', speed=default_speed_slow) #
    c.move('flask_separator', 'rotavap', 40, dest_port='evaporate', speed=default_speed_slow, through_nodes='drying_col') #

    #c.connect('carousel_top', 'carousel_bottom', src_port='route', dest_port='route')
    #dry product of second step
    evaporate_to_dryness(20, 260, 1, 680, 500, 10, 1800, 900, 900, rv_temp_one) #theres some methanol in the reaction as well...

    c.move('reactor_reactor', 'waste_reactor', tot_volume, initial_pump_speed=60, mid_pump_speed=50, end_pump_speed=70)
    c.move('reactor_reactor', 'waste_reactor', 50, initial_pump_speed=60, mid_pump_speed=50, end_pump_speed=70)
    c.camera.change_recording_speed(1000)
    clean_separator()
    clean_hose(5)

    # ==================================================================================================================================
    ################
    #esterification#
    ################


    c.camera.change_recording_speed(1000)
    #Cleaning the relevant glassware
    clean_reactor('flask_water', 100) # parameters: Source flask, volume in mL
    clean_reactor('flask_MeOH_dry', 300) # parameters: Source flask, volume in mL
    clean_filter('flask_water', 50) # parameters: Source flask, Temperature in C
    clean_reactor('flask_ether', 300) # Remember to uncomment part of the function
    clean_filter('flask_MeOH_dry', 50) # parameters: Source flask, Temperature in C
    # c.camera.change_recording_speed(10000)
    # S BREAKPOINT()
    c.camera.change_recording_speed(250)



    clean_hose(5)
    # check the code for this
    c.chiller.set_temp('reactor_reactor', ice_bath)
    c.chiller.start_chiller('reactor_reactor')
    transfer_from_rotavap('reactor_reactor', 'flask_DCM', volume_DCM, default_speed_slow, 25)
    transfer_from_rotavap('reactor_reactor', 'flask_DCM', volume_DCM, default_speed_slow, 25)
    c.chiller.wait_for_temp('reactor_reactor')
    tot_volume = 2 * volume_DCM
    c.stirrer.set_stir_rate('reactor_reactor', 400)
    c.stirrer.stir('reactor_reactor')

    c.camera.change_recording_speed(250)
    c.stirrer.set_stir_rate('flask_EDCI_in_DCM', 400)
    c.stirrer.stir('flask_EDCI_in_DCM')
    c.move('flask_DCM', 'flask_EDCI_in_DCM', 120, initial_pump_speed=default_speed_slow, mid_pump_speed=default_speed_fast, end_pump_speed=default_speed_fast)
    c.wait(300)

    c.move('flask_EDCI_in_DCM', 'reactor_reactor', volume_EDCI_in_DCM, initial_pump_speed=default_speed_slow , mid_pump_speed=default_speed_slow, end_pump_speed=10)
    c.stirrer.stop_stir('flask_EDCI_in_DCM')
    c.camera.change_recording_speed(200); tot_volume += volume_EDCI_in_DCM
    c.wait(600)
    c.move('flask_NHS_in_ACN', 'reactor_reactor', volume_NHS_in_ACN, initial_pump_speed=default_speed_slow, mid_pump_speed=default_speed_slow, end_pump_speed=default_speed_dead_slow)
    c.camera.change_recording_speed(100); tot_volume += volume_NHS_in_ACN

    c.move('flask_DCM', 'reactor_reactor', 3, speed=default_speed_slow)
    rotavap_cleaning(30, 'flask_water') # parameters: Volume in mL, Source flask
    rotavap_cleaning(60, 'flask_MeOH_dry')
    rotavap_cleaning(60, 'flask_ether')
    c.wait(600)
    c.chiller.set_temp('reactor_reactor', 28)  # Better to keep temperature controlled because of uncontrollable evaporation
    c.camera.change_recording_speed(10000)
    c.wait(72000) # 20h reacting

    c.camera.change_recording_speed(100)
    c.stirrer.stop_stir('reactor_reactor')

    ####################################################
    # WASHING / LIQUID SEPARATION and moving to rotary #
    ####################################################

    # WASHING REMOVED BECAUSE OF HYDROLYSIS

    #####################################################
    c.move('reactor_reactor', 'rotavap', (tot_volume + 20), speed=40, dest_port='evaporate') # Revert back to 20 if you uncomment the washing above

    # ==Cleaning up the reactor a  little bit and moving to rotavap===========
    c.move('flask_DCM', 'reactor_reactor', 25, speed=40)
    c.stirrer.set_stir_rate('reactor_reactor', 800)
    c.stirrer.stir('reactor_reactor')
    c.wait(60)
    c.stirrer.stop_stir('reactor_reactor')
    c.move('reactor_reactor', 'rotavap', 30, speed=40)
    # =======end of cleaning==================================================
    c.camera.change_recording_speed(500)
    # these values can be reduced for time sake
    evaporate_to_dryness(230, 50, 30, 480, 110, 3, 2400, 1800, 900, 36)
    clean_hose(5)
    c.chiller.stop_chiller('filter_filter_top')

    # S BREAKPOINT()

    # ================================================================================================================================================
    #######################################
    #Purification by Liquid Chromatography#
    #######################################
    c.camera.change_recording_speed(500)
    # # prime column
    c.move(flask_eluent, 'waste_chroma', 3, initial_pump_speed=eluent_aspiration_speed, mid_pump_speed=eluent_aspiration_speed, end_pump_speed=priming_speed, through_nodes='column_1')
    c.move(flask_eluent, 'waste_chroma', priming_volume, initial_pump_speed=eluent_aspiration_speed, mid_pump_speed=eluent_aspiration_speed, end_pump_speed=priming_speed,
           through_nodes='column_1')
    # S BREAKPOINT()
    # Disolve back to move into the column
    c.move('flask_DCM', 'rotavap', 30, speed=default_speed_fast)
    c['rotavap'].temperature_sp = 30
    c['rotavap'].start_heater()

    c['rotavap'].lift_down()
    c['rotavap'].set_interval = 15
    c['rotavap'].rotation_speed_sp = 150
    c['rotavap'].start_rotation()
    c.wait(1800)
    c['rotavap'].stop_rotation()

    # load sample
    c.move('rotavap', 'waste_chroma', 40, initial_pump_speed=5, mid_pump_speed=default_speed_fast, end_pump_speed=default_speed_fast,
           through_nodes='column_1', src_port='evaporate')

    # wash a second time with 20 mL
    c.move('flask_DCM', 'rotavap', 20, speed=default_speed_fast)

    c['rotavap'].start_rotation()
    c.wait(160)
    c['rotavap'].stop_rotation()
    c.move('rotavap', 'waste_chroma', 25, initial_pump_speed=5, mid_pump_speed=default_speed_fast, end_pump_speed=default_speed_fast,
           through_nodes='column_1', src_port='evaporate')
    # ==============================

    # wash other two times with 10 mL
    for _ in range(2):
        c['rotavap'].start_rotation()
        c.move(flask_eluent, 'rotavap', volume_loading, speed=default_speed_fast)
        c.wait(60)
        c['rotavap'].stop_rotation()
        c.move('rotavap', 'waste_chroma', volume_loading, initial_pump_speed=25, mid_pump_speed=default_speed_fast, end_pump_speed=default_speed_fast,
               through_nodes='column_1', src_port='evaporate')

    c.move('rotavap', 'waste_chroma', 8, initial_pump_speed=25, mid_pump_speed=default_speed_fast, end_pump_speed=default_speed_fast,
           through_nodes='column_1')
    # ================================
    c.camera.change_recording_speed(100)
    # S BREAKPOINT()
    c['rotavap'].stop_heater()
    c['rotavap'].lift_up()

    ###############
    # TESTING ##### COMMENT THE CODE BELOW  WHEN DONE!
    ###############

    # FOR(66) {
        # c.move(flask_eluent, column_1, 15, default_speed_fast, eluent_aspiration_speed, elution_speed)
    # }
    # S BREAKPOINT()
    ###############
    # END TEST ####
    ###############


    # Elute dead volume
    c.move(flask_eluent, 'flask_column_bottom', dead_fraction_volume, initial_pump_speed=eluent_aspiration_speed, mid_pump_speed=default_speed_fast, end_pump_speed=elution_speed,
           through_nodes='column_1')
    # Collect fractions
    c.move(flask_eluent, 'flask_column_bottom', collect_fraction_volume, initial_pump_speed=eluent_aspiration_speed, mid_pump_speed=default_speed_fast, end_pump_speed=elution_speed,
           through_nodes='column_1')
    c.connect('column_1', 'waste_chroma', src_port='out')
    #rotavap_cleaning(40, 'flask_MeOH_dry')
    rotavap_cleaning(60, 'flask_DCM')

    for _ in range(2):
        c.move('flask_column_bottom', 'rotavap', 200, speed=default_speed_fast)
        evaporate_to_dryness(150, 150, 10, 525, 420, 50, 1800, 1800, 60, 36)  # TODO not hard code that

    evaporate_to_dryness(1, 1, 10, 900, 800, 5, 60, 60, 1800, 36)

    reduced_clean(5)

    # c.camera.change_recording_speed(1000000)
    # S BREAKPOINT()


    # # ============================================================================================================================
    # #################
    # #Crystallization#
    # #################

    # c.chiller.set_temp('reactor_reactor', crist_bath)
    # c.chiller.start_chiller('reactor_reactor')

    # #############################################
        # # Disolve back to move into the filter
    # #############################################
    # c.move('flask_ether', rotavap, 80, speed=default_speed_fast)
    # c.move('flask_ether', rotavap, 10, speed=default_speed_fast);
    # c['rotavap'].temperature_sp =30
    # c['rotavap'].start_heater()

    # c['rotavap'].lift_down()
    # c['rotavap'].set_interval = 15
    # c['rotavap'].rotation_speed_sp =150
    # c['rotavap'].start_rotation()
    # c.wait(1800)
    # c['rotavap'].stop_rotation()
    # c['rotavap'].stop_heater()

    # # ==============================================

    # # c.chiller.wait_for_temp('filter_filter_top')

    # # # Redisolve in 50:50 mol% of Et2O/MeOH and allow precipitation in the Jacketed filter at 0 C
    # # c.move('flask_MeOH_dry', 'waste_rotary', 5)
    # # c.move('flask_Ar_M', 'waste_rotary', 20)
    # # c.move('flask_MeOH_dry', 'waste_separator', 10)
    # # c.move('flask_Ar_M', 'waste_rotary', 10)

    # prime_filter(crist_bath, 'flask_ether', stirring_rate_diazirine)
    # c.move('flask_ether', filter_filter_top, 10, speed=default_speed_fast)
    # c.stirrer.stop_stir('filter_filter_top')
    # c.move(rotary, filter_filter_top, 100, default_speed_fast, default_speed_slow, default_speed_fast)
    # c['rotavap'].lift_up()
    # c.wait(10800)

    # # # Now filtration and drying
    # c.move('filter_filter_top', reactor_reactor, 140, 60, 10, 60); # when sure of what you're trashing change reactor_reactor to waste_reactor
    # c.chiller.set_temp('filter_filter_top', 28)
    # c.chiller.wait_for_temp('filter_filter_top')
    # S SWITCH_VACUUM(filter_filter_top, vacuum)
    # c.wait(300)
    # S SWITCH_VACUUM(filter_filter_top, backbone)
    # c.chiller.stop_chiller('filter_filter_top')

    # # Redisolve in DCM and evaporate
    # c.move(flask_DCM, 'filter_filter_top', 100, speed=default_speed_fast)
    # c.stirrer.set_stir_rate('filter_filter_top', 200)
    # c.stirrer.stir('filter_filter_top')
    # c.wait(300)
    # c.stirrer.stop_stir('filter_filter_top')
    # c.move('filter_filter_top', rotary, 120, default_speed_fast, default_speed_slow, default_speed_fast)

    # evaporate_to_dryness(120, 50, 10, 480, 110, 3, 1800, 1800, 900, 36)

    # ####################################################
    # # WASHING / LIQUID SEPARATION and moving to rotary #
    # ####################################################

    # # FOR(1) {
        # # c.move(reactor_reactor, flask_separator, 'all', 60, 60, 60)
        # # c.move('flask_ether', flask_separator, volume_brine, 60, 60, 60)
        # # separate_phases(reactor_reactor, 'waste_separator', 150, -250); # The correct one should be 180 mL
    # # }
    # # c.move(reactor_reactor, flask_separator, "all", 60, 60, 60)
    # # c.move('flask_ether', flask_separator, volume_brine, 60, 60, 60)
    # # c.move('waste_separator', 'waste_rotary', 30, 60, 60, 60); # To clear the tubing from water
    # # c.move('flask_MeOH_dry', 'waste_rotary', 5, 60, 60, 60); # To clear the tubing from water
    # # S SWITCH_CARTRIDGE(rotavap, 3)
    # # separate_phases(rotavap, 'waste_separator', 150, -250); # The correct one should be 180 mL
    # # c.chiller.stop_chiller('reactor_reactor')

    # # # Cleaning from residual product
    # # c.move(flask_DCM, reactor_reactor, 15, 40, 40, 40);
    # # =========================================================================================================

    c.move('flask_Ar_R', 'waste_chroma', 350, initial_pump_speed=eluent_aspiration_speed, mid_pump_speed=default_speed_fast, end_pump_speed=elution_speed,
           through_nodes='column_1')


    c.camera.change_recording_speed(1000000)
