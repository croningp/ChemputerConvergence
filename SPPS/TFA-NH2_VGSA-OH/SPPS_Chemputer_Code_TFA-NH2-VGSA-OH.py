from os import path

import ChemputerAPI
import SerialLabware
import sys
import string

from chempiler import Chempiler

# change this to experiment name
experiment_name = "SPPS_Chemputer_TFA-NH2-VGSA-OH"
root = path.abspath(path.dirname(__file__))
output_dir = path.join(root, 'logs')
# change this to graphML file name
graphml_file = path.join(root, 'SPPS_Chemputer_Graph.json')

c = Chempiler(experiment_name, graphml_file, output_dir, simulation=False, device_modules=[ChemputerAPI, SerialLabware])

########################################################################################################################
#                                                                                                                      #
#       PEPTIDE                                                                                                        #
#                                                                                                                      #
########################################################################################################################

peptide = ["Val", "Gly", "Ser"]              # Amino acids to be conjugated to the resin (excl. amino acid the resin is pre-functionalised with)
											 # List N-to-C terminus according to nomenclature rules. Will be synthesised C-to-N terminus.
total_volume_aa = [0, 0, 0]                  # Function for keeping track of volumes need of each amino acid 

########################################################################################################################
#                                                                                                                      #
#       CONSTANTS                                                                                                      #
#                                                                                                                      #
########################################################################################################################


# volumes
filter1_dead_volume = 2.5                    # volume needed to fill filter1 bottom
filter2_dead_volume = 14.0                   # volume needed to fill filter2 bottom
priming_volume_default = 1.5                 # mL volume used to prime tubing from stock bottle to connected valve

volume_swell_resin_solvent = 9.0             # mL DMF (ultra-pure)
volume_wash_resin_solvent = 9.0              # mL DMF (ultra-pure)
volume_Fmoc_deprotection = 9.0               # mL 20% piperidine in DMF
volume_coupling_reagent = 4.0                # mL 0.475 M HBTU in DMF
volume_coupling_additive = 0.0               # mL 1 M HOBt in DMF
volume_coupling_base = 2.0                   # mL 2 M DIPEA in NMP
volume_amino_acid = 4.0                      # mL 0.5 M aa (Fmoc and side-chain proteced) in DMF, also applies to NHS-dazirine solution
volume_precleavage_solvent = 9.0             # mL DCM for resin washing after the full peptide was assembled
volume_cleavage_solution = 10.0              # mL TFA/TIPS/H2O 95/2.5/2.5 cleavage and side-chain deprptection. TIPS/H2O for carbocation (free PGs) scavenging.                  
volume_cleavage_solution_wash = 0.5		     # mL of cleavage mixture to wash the resin after cleavage
volume_ether_precipitation = 150.0           # mL max volume of the jacketed filter used was 200 mL, according to Stefanie 250 mL ether were used for the precipitation of just the VGSA-TFA salt, Diana used 30 mL ether for the precipitation of the diazirine-VGSA construct.
volume_ether_wash = 30.0                     # mL
volume_dissolve_peptide_H2O = 6.0            # mL the biotage used 10 mL water only
volume_dissolve_peptide_MeCN = 1.5           # mL
volume_diazirine_solution = 8.0				 # mL
volume_DIPEA_in_DCM = 2.0			     	 # mL
volume_NHS_diazirine = 4.0 					 # mL

total_volume_swell_resin_solvent = 0         # mL 
total_volume_wash_resin_solvent = 0          # mL 
total_volume_Fmoc_deprotection = 0           # mL
total_volume_coupling_reagent = 0            # mL
total_volume_coupling_additive = 0           # mL
total_volume_coupling_base = 0               # mL
total_volume_cleavage_solution = 0           # mL
total_volume_TFA = 0                         # mL
total_volume_TIPS = 0                        # mL
total_volume_H2O = 0                         # mL
total_volume_ether = 0                       # mL
total_volume_MeCN = 0                        # mL
total_volume_DMF = 0                         # mL ultra-pure DMF needed for protocol
total_volume_DMF_cleaning = 0                # mL DMF needed for cleaning protocol (i.e. washing tubes)
total_volume_H2O_cleaning = 0                # mL water needed for cleaning protocol (i.e. washing tubes)
total_volume_NHS_diazirine = 0               # mL of 0.5 M NHC-diazirien solution needed
total_volume_precleavage_solvent = 0 		 # mL of DCM	
total_volume_DIPEA_in_DCM = 0
no_of_resin_washes = 5                       # number of times resin is washed with solvent in between steps

# stirring rates
stirring_rate_default = 250                  # RPM
stirring_rate_slow = 50						 # RPM 
stirring_rate_fast = 500					 # RPM

# wait times
wait_time_swell_resin = 3600                 # 60 min
wait_time_Fmoc_deprotection_stage_1 = 180    # 3 min 
wait_time_Fmoc_deprotection_stage_2 = 720    # 12 min
wait_time_coupling = 3600             		 # 1 h
wait_time_wash_resin = 45                    # 45 s
wait_time_dry_resin = 900                    # 15 min
wait_time_cleavage = 10800                   # 3 h
wait_time_sedimentation = 300              	 # 5 min
wait_time_precipitation = 3600               # 1 h precipitation time for the peptide
wait_time_dry_peptide = 300					 # 5 min

# temperatures
room_temperature = 20                        # °C
precipitation_temperature = -25              # °C

# pumping speeds
default_speed_very_slow = 5                  # mL/min
default_speed_slow = 20                      # mL/min
default_speed_fast = 50                      # mL/min
default_speed_very_fast = 120				 # mL/min

########################################################################################################################
#                                                                                                                      #
#       FUNCTIONS                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def clean_org(volume = 2, no_of_times = 2, waste = "Waste_1"):
	"""
	Cleans backbone with DMF
	"""
	global total_volume_DMF_cleaning

	for i in range(no_of_times):    
		c.move("DMF_cleaning", waste, volume, speed=default_speed_very_fast)
	total_volume_DMF_cleaning +=  volume * no_of_times

def clean_org_DCM(volume = 2, no_of_times = 2, waste = "Waste_3"):
	"""
	Cleans backbone with DCM
	"""
	global total_volume_precleavage_solvent

	for i in range(no_of_times):    
		c.move("DCM", waste, volume, speed=default_speed_very_fast)
	total_volume_precleavage_solvent +=  volume * no_of_times

def clean_aq(volume = 2, no_of_times = 2):
	"""
	Cleans backbone with H2O.
	"""
	global total_volume_H2O_cleaning

	for i in range(no_of_times):    
		c.move("H2O_cleaning", "Waste_8", volume, speed=default_speed_very_fast)
		c.move("H2O_cleaning", "Waste_1", volume, speed=default_speed_very_fast)

	total_volume_H2O_cleaning +=  volume * no_of_times

def accurate_transfer_aq(source, destination, volume, priming_volume=priming_volume_default):
	
	c.move(source, "Pump_7", priming_volume, speed=default_speed_slow) 
	c.move("Pump_7", "Waste_7", priming_volume, speed=default_speed_slow) 
	c.move(source, destination, volume, default_speed_very_slow)
	for i in range(3):
		c.move("Waste_7", "Waste_7", 10, speed=default_speed_very_fast)   # To make sure tube has no liquid in it     
	c.move("Waste_7", destination, 10, speed=default_speed_fast)           	 # "air-push" to make sure all liquid is delivered to destination

	return volume + priming_volume

def air_push_to_filter1():
	for i in range(3):
		c.move("Waste_3", "Waste_3", 10, speed=default_speed_very_fast) # To make sure tube has no liquid in it
	c.move("Waste_3", "Reactor_1", 10, speed=default_speed_very_fast, dest_port="top") # "air-push" to make sure all liquid is delivered to destination
	
def prime_tubing_to_filter1(flask, priming_volume = priming_volume_default):
	c.move(flask, "Pump_3", priming_volume, speed=default_speed_fast)
	c.move("Pump_3", "Waste_3", priming_volume, speed=default_speed_fast) # prime tube from source (reagent flask) to destination (filter 1)
	return priming_volume

def filter_react(source, volume, reaction_time, stirring_rate = stirring_rate_default, no_of_times = 1, drain_to = "Waste_3", drain = True, solvent_filter_bottom = "DMF", fill_bottom = True, clean_backbone = "o"): 
	"""
	Adds solution to filter, stirs, and drains. Returns required reagent volume.

	Args:

	source (str): Node from which volume is to be withdrawn

	volume (float): Total volume to move to Reactor_1 in mL

	reaction_time (int): Time to wait in seconds

	stirring rate: in rpm

	no_of_times (int): Number of fill, react, drain cycles

	drain_to (str): Node to which volume is moved after reaction

	drain (bool): If true, filter will be emptied to drain_to location.

	solvent_filter_bottom (str): Liquid which is used to fill filter bottom to prevent percolation
	
	fill_bottom (boolean): If False, filter bottom is kept empty during the reaction

	clean_backbone (str): Options are "o" (default, clean with DMF), "a" (clean with H2O) or "no" (don't clean backbone)

	"""
	global total_volume_DMF

	for i in range(no_of_times):
		c.camera.change_recording_speed(20)

		# Fill filter_bottom with solvent/reactant if selected, fill top with reactant
		if fill_bottom == True:
			c.move(solvent_filter_bottom, "Reactor_1", filter1_dead_volume, speed=default_speed_fast, dest_port="bottom")
			total_volume_DMF += filter1_dead_volume
		
		c.move(source, "Reactor_1", volume, speed=default_speed_fast, dest_port="top")

		# Stir
		c.stirrer.set_stir_rate("Reactor_1", stirring_rate)
		c.stirrer.stir("Reactor_1")
		
		# Clean backbone with solvent
		if clean_backbone.lower () == "o":
			clean_org() 
		elif clean_backbone.lower () == "a":
			clean_aq()
		elif clean_backbone.lower () == "no":
			pass
		else: 
			print ("Exception, cleaning with organic")
			clean_org() 
		
		# Wait for reaction to complete
		c.camera.change_recording_speed(100)
		c.wait(reaction_time)
		c.camera.change_recording_speed(20)

		# Drain filter
		c.stirrer.stop_stir("Reactor_1")
		if drain == True:
			if fill_bottom == True:
				drain_filter_1(filter1_dead_volume + volume)
			else:
				drain_filter_1(volume)
			dry("Reactor_1", 300)

	return volume * no_of_times # For calculating reagent stock volumes needed

def drain_filter_1(draining_volume):
	"""
	Drains filter 1 efficiently
	Args: 
	draining_voume (float): volume of liquid that is to be removed
	"""
	i = draining_volume
	c.stirrer.set_stir_rate("Reactor_1", stirring_rate_slow)
	c.stirrer.stir("Reactor_1")

	while i > 0:
		c.move("Reactor_1", "Pump_3", 10, speed=default_speed_fast)
		c.wait(40)
		c.move("Pump_3", "Waste_3", 10, speed=default_speed_very_fast)
		i -= 1

def drain_filter_2(draining_volume, dest="Waste_4"):
	"""
	Drains filter 2 efficiently
	Args: 
	draining_voume (float): volume of liquid that is to be removed
	"""
	i = draining_volume * 4

	while i > 0:
		c.move("Reactor_2", "Pump_4", 10, speed=default_speed_slow)
		c.wait(20)
		c.move("Pump_4", dest, 10, speed=default_speed_very_fast)
		i -= 10
	

#function that takes one amino acid reagent, adds it to the filter, adds coupling system, stirs and drains
def filter_coupling(source, volume = volume_amino_acid, reaction_time = wait_time_coupling, stirring_rate = stirring_rate_default, no_of_times = 1):
	"""
	Performs peptide coupling.

	Args:

	source (str): Node from which amino acid is to be withdrawn

	volume (float): Volume of amino acid moved to Reactor_1 in mL

	reaction_time (int): Time to wait in seconds

	stirring rate: in rpm.

	no_of_times (int): Number of fill, react, drain cycles. Use 2 for double-coupling.

	drain_to (str): Node to which volume is moved after reaction.

	solvent_filter_filter_bottom (str): Liquid which is used to prevent percolation
	
	fill_bottom (boolean): If False, filter_filter_bottom is kept empty during the reaction

	"""
	global total_volume_DMF
	global total_volume_coupling_reagent         
	global total_volume_coupling_additive          
	global total_volume_coupling_base

	for i in range(no_of_times):
		
		# Fill filter_bottom with DMF
		c.camera.change_recording_speed(20)
		c.move("DMF", "Reactor_1", filter1_dead_volume, speed=default_speed_fast, dest_port="bottom")
		total_volume_DMF += filter1_dead_volume # Add to volume of ultra-pure DMF needed for run

		total_volume_aa[position] += prime_tubing_to_filter1(source)
		
		# Fill Reactor_1 with amino acid
		c.move(source, "Reactor_1", volume, speed=default_speed_slow, dest_port="top")
	   
		# Stir
		c.stirrer.set_stir_rate("Reactor_1", stirring_rate)
		c.stirrer.stir("Reactor_1")

		# Clean tubes with DMF
		clean_org(waste = "Waste_1") 

		# Fill Reactor_1 with coupling reagent
		total_volume_coupling_reagent += prime_tubing_to_filter1("HBTU")
		c.move("HBTU", "Reactor_1", volume_coupling_reagent, speed=default_speed_slow, dest_port="top")
		total_volume_coupling_reagent += volume_coupling_reagent

		# Clean tubes with DMF
		clean_org(waste = "Waste_2")

		# Fill Reactor_1 with coupling base
		total_volume_coupling_base += prime_tubing_to_filter1("DIPEA")
		c.move("DIPEA", "Reactor_1", volume_coupling_base, speed=default_speed_slow, dest_port="top")
		total_volume_coupling_base += volume_coupling_base 
		air_push_to_filter1()

		# Clean tubes with DMF
		clean_org(waste = "Waste_3") 

		# Wait for reaction to complete
		c.camera.change_recording_speed(100)
		c.wait(reaction_time)
		c.camera.change_recording_speed(20)

		# Drain filter
		c.stirrer.stop_stir("Reactor_1")
		drain_filter_1(filter1_dead_volume + volume + volume_coupling_reagent + volume_coupling_base)
		dry("Reactor_1", 300)

def dry(filter, time):
	"""
	Applies vaccuum to filter.

	Args:

	filter (str): Filter name.

	time (int): Drying time in seconds.
	
	"""

	c.wait(5) # avoids Actuation Failure if the function is called twice in a row. 

	if filter == "Reactor_1":
		c.connect(filter, "Vacuum_1")
		c.wait(time)
		c.connect(filter, "Pump_3")  
		c.wait(5)  # avoids Actuation Failure if the function is called twice in a row.
	if filter == "Reactor_2":
		c.connect(filter, "Vacuum_2")
		c.wait(time)
		c.connect(filter, "Pump_4")  
		c.wait(5)  # avoids Actuation Failure if the function is called twice in a row.

def print_table():
	from prettytable import PrettyTable

	print("\n")
	t = PrettyTable(["Reagent Type", "Step", "Volume (mL)", " ", "Total Volume (mL)"])
	t.align["Reagent Type"] = "r"
	t.align["Step"] = "c"
	t.align["Volume (mL)"] = "r"

	t.add_row(["Solvent", "Resin swelling", total_volume_swell_resin_solvent, "", ""])
	t.add_row(["Solvent", "Resin washing", total_volume_wash_resin_solvent, "", ""])
	t.add_row(["Base", "Fmoc deprotection solution", total_volume_Fmoc_deprotection, "", ""])

	position = -1
	for aa in (peptide):
		t.add_row([peptide[position], "Amino acid coupling", total_volume_aa[position], "", ""])
		position = position -1

	t.add_row(["NHS_diazirine", "NHS_diazirine coupling", total_volume_NHS_diazirine, "", ""])
	t.add_row(["Coupling reagent", "Amino acid coupling", total_volume_coupling_reagent, "", ""])
	t.add_row(["Coupling additive", "Amino acid coupling", total_volume_coupling_additive, "", ""])
	t.add_row(["Coupling base", "Amino acid coupling", total_volume_coupling_base, "", ""])
	t.add_row(["DCM", "Precleavage wash", total_volume_precleavage_solvent, "", ""])
	t.add_row(["TFA/scavenger cocktail", "Resin and side-chain deprotection", total_volume_cleavage_solution, "", ""])
	t.add_row(["TFA", "TFA/scavenger cocktail component", total_volume_TFA, "", ""])
	t.add_row(["TIPS", "TFA/scavenger cocktail component", total_volume_TIPS, "", ""])
	t.add_row(["H2O (HPLC-grade)", "TFA/scavenger cocktail component", total_volume_H2O, "", ""])
	t.add_row(["Ether", "Peptide precipitation, wash", total_volume_ether, "", ""])
	t.add_row(["MeCN", "Solubilise peptide", total_volume_MeCN, "", ""])
	t.add_row(["Solvent/Reactant", "Fill filter bottom", total_volume_DMF, "If DMF is used to swell and wash resin", total_volume_DMF + total_volume_swell_resin_solvent + total_volume_wash_resin_solvent])
	t.add_row(["DMF (cleaning)", "Backbone wash organic", total_volume_DMF_cleaning, "", ""])
	t.add_row(["H2O (dist.)", "Backbone wash aqueous, Solubilise peptide", total_volume_H2O_cleaning, "", ""])
	t.add_row(["Base in DCM", "DIPEA in DCM for NHS_diazirine coupling", total_volume_DIPEA_in_DCM, "", ""])
	c.logger.info(t)


########################################################################################################################
#                                                                                                                      #
#       HOUSEKEEPING                                                                                                   #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

c.start_recording() # Start video recording
c.camera.change_recording_speed(20)

clean_org(5, 2) # comment out if you know that the bb is clean

########################################################################################################################
#                                                                                                                      #
#       SWELLING RESIN WITH DMF                                                                                        #
#       add resin to reactor                                                                                           #
#                                                                                                                      #
########################################################################################################################
c.logger.info("Swelling resin with DMF.")

total_volume_swell_resin_solvent += prime_tubing_to_filter1("DMF") # prime DMF (ultra-pure) tube

total_volume_swell_resin_solvent += filter_react("DMF", volume_swell_resin_solvent, wait_time_swell_resin)

########################################################################################################################
#                                                                                                                      #
#       RESIN Fmoc DEPROTECTION                                                                                        #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################
c.logger.info("Fmoc deprotection of aa on pre-functionalised resin.")

total_volume_Fmoc_deprotection += prime_tubing_to_filter1("Piperidine") # prime piperidine tube

total_volume_Fmoc_deprotection += filter_react("Piperidine", volume_Fmoc_deprotection, wait_time_Fmoc_deprotection_stage_1)
total_volume_Fmoc_deprotection += filter_react("Piperidine", volume_Fmoc_deprotection, wait_time_Fmoc_deprotection_stage_2)

total_volume_wash_resin_solvent += filter_react("DMF", volume_wash_resin_solvent, wait_time_wash_resin, no_of_times = no_of_resin_washes, fill_bottom = False, clean_backbone = "no")

########################################################################################################################
#                                                                                                                      #
#       COUPLING (double-coupling)                                                                                     #
#                                                                                                                      #
#       and                                                                                                            #
#                                                                                                                      #
#       Fmoc DEPROTECTION (two-stage)                                                                                  #
#                                                                                                                      #
########################################################################################################################
c.logger.info("Coupling amino acid.")

position = -1               # Position of next amino acid to be coupled from back of list
for a in (peptide):

	for i in range(2):      # Double-coupling

		# Select amino acid flask
		flask_next_amino_acid = peptide[position]
		c.logger.info("Coupling " + peptide[position] + ".")

		filter_coupling(flask_next_amino_acid)
		total_volume_aa[position] += volume_amino_acid # Add used volume to list of volumes of each amino acid

		# DMF wash of resin to remove coupling reagents
		c.logger.info("DMF wash after coupling.")
		total_volume_wash_resin_solvent += filter_react("DMF", volume_wash_resin_solvent, wait_time_wash_resin, no_of_times = no_of_resin_washes, fill_bottom = False, clean_backbone = "no")
		
	# Fmoc deprotection
	c.logger.info("Fmoc deprotection stage 1 (" + str(wait_time_Fmoc_deprotection_stage_1) + ").")
	total_volume_Fmoc_deprotection += filter_react("Piperidine", volume_Fmoc_deprotection, wait_time_Fmoc_deprotection_stage_1)
	c.logger.info("Fmoc deprotection stage 2 (" + str(wait_time_Fmoc_deprotection_stage_2) + ").")
	total_volume_Fmoc_deprotection += filter_react("Piperidine", volume_Fmoc_deprotection, wait_time_Fmoc_deprotection_stage_2)

	# DMF wash of resin to remove piperidine and Fmoc residues
	c.logger.info("DMF wash after Fmoc deprotection to remove piperidine and Fmoc residues.")
	
	total_volume_wash_resin_solvent += filter_react("DMF", volume_wash_resin_solvent, wait_time_wash_resin, no_of_times = no_of_resin_washes, fill_bottom = False, clean_backbone = "no")

	position = position - 1

#DMF wash is performed after last AA coupling and before NHS_diazirine coupling
########################################################################################################################
#                                                                                                                      #
#       WASH WITH DMF                                                                                                  #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################
c.logger.info("DMF wash after final coupling.")

total_volume_wash_resin_solvent += filter_react("DMF", volume_wash_resin_solvent, wait_time_wash_resin, no_of_times = 3, fill_bottom = False, clean_backbone = "no")

dry("Reactor_1", 300)

# Backbone cleaning with DCM before the DCM wash in order to minimize DMF contamination
for i in range(3):
	c.move("DCM","Pump_7", 5, speed=default_speed_very_fast)
	c.move("Pump_7","Waste_1", 5, speed=default_speed_very_fast)
	total_volume_precleavage_solvent += 5

#Wash the resing with DCM
total_volume_precleavage_solvent += filter_react("DCM", volume_precleavage_solvent, wait_time_wash_resin, no_of_times = no_of_resin_washes, fill_bottom = False, clean_backbone = "no")

########################################################################################################################
#                                                                                                                      #
#       CLEAVAGE WITH TFA FOLLOWED BY PRECIPITATION WITH ETHER                                                         #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################
c.logger.info("Cleavage with TFA followed by precipitation with ether.")

#Start chiller and cool diethyl ether for precipitation (dietyl ether at -25 °C needs to be ready right after the cleavage in order to keep precise timing)
c.chiller.set_temp("Reactor_2", precipitation_temperature) 
c.chiller.start_chiller("Reactor_2")
c.move("Ether", "Waste_4", priming_volume_default, speed=default_speed_fast) # prime tube
total_volume_ether += priming_volume_default
c.stirrer.set_stir_rate("Reactor_2", stirring_rate_slow)
c.stirrer.stir("Reactor_2")
c.move("Ether", "Reactor_2", filter2_dead_volume, speed=default_speed_slow, dest_port="bottom")
c.move("Ether", "Reactor_2", volume_ether_precipitation, speed=default_speed_fast, dest_port="top") 
total_volume_ether += volume_ether_precipitation + filter2_dead_volume

for i in range(3):
	c.move("Waste_4", "Waste_4", 10, speed=default_speed_fast) # To make sure tube has no liquid in it
c.move("Waste_4", "Reactor_2", 10, speed=default_speed_fast, dest_port="top") # "air-push" to make sure no more ether is in the tubing which otherwise may lead to clogging

#Prepare the cleavage cocktail
c.move("TFA", "Waste_7", 1, speed=default_speed_slow)
c.move("TFA", "Cleavage_mix", 19, speed=default_speed_slow)
total_volume_TFA += 20

c.move("TIPS", "Waste_7", 1.5, speed=default_speed_slow)
c.move("TIPS", "Cleavage_mix", 0.6, speed=default_speed_slow)
total_volume_TIPS += 2.1

c.move("H2O", "Waste_7", 1.5, speed=default_speed_slow)
c.move("H2O", "Cleavage_mix", 0.6, speed=default_speed_slow)
total_volume_H2O += 2.1

#mix cleavage cocktail
for i in range(3):
	c.move("Cleavage_mix", "Cleavage_mix", 10, speed=default_speed_very_fast)

c.chiller.wait_for_temp("Reactor_2")

c.logger.info("Ready for cleavage.")
#c.breakpoint()

#Cleavage and collection
c.logger.info("Start of cleavage with TFA followed directly by collection.")
total_volume_cleavage_solution += prime_tubing_to_filter1("Cleavage_mix") # prime bb with cleavage cocktail
total_volume_cleavage_solution += filter_react("Cleavage_mix", volume_cleavage_solution, wait_time_cleavage, fill_bottom = False, drain = False, clean_backbone = "no")
c.move("Reactor_1", "Reactor_2", volume_cleavage_solution + 20, speed=default_speed_slow, dest_port="top")
c.move("Reactor_1", "Reactor_2", 10, speed=default_speed_fast, dest_port="top")

for i in range(3): # washing the filter_1 three tims with a small amount of cleavage cocktail
	total_volume_cleavage_solution += filter_react("Cleavage_mix", volume_cleavage_solution_wash, wait_time_wash_resin, fill_bottom = False, drain = False, clean_backbone = "no")
	for a in range(2):
		c.move("Reactor_1", "Reactor_2", 5, speed=default_speed_slow, dest_port="top")

#Precipitation (and some backbone cleaning)
c.stirrer.stop_stir("Reactor_2")

#cleaning the bb with water to remove TFA residues immediately
for i in range(3):
	c.move("H2O_cleaning", "Waste_7", 5, speed=default_speed_very_fast)
	total_volume_H2O_cleaning += 5

#cleaning the bb with ether to remove water residues 
for i in range(3):
	c.move("Ether", "Waste_2", 5, speed=default_speed_very_fast)
	c.move("Ether", "Waste_7", 5, speed=default_speed_very_fast)
	total_volume_ether +=  10

c.wait(wait_time_precipitation)

drain_filter_2(volume_cleavage_solution + volume_ether_precipitation + filter2_dead_volume, dest="Waste_4")

# Wash peptide with ether
for i in range(4):
	# Add ether to filter
	c.move("Ether", "Reactor_2", filter2_dead_volume, speed=default_speed_fast, dest_port="bottom") 
	c.move("Ether", "Reactor_2", volume_ether_wash, speed=default_speed_slow, dest_port="bottom")
	total_volume_ether += volume_ether_wash + filter2_dead_volume

	# Stir
	c.stirrer.set_stir_rate("Reactor_2", stirring_rate_fast)
	c.stirrer.stir("Reactor_2")
	c.wait(60)

	# Sediment and drain
	c.stirrer.stop_stir("Reactor_2")
	c.wait(wait_time_sedimentation)
	drain_filter_2(volume_ether_wash + filter2_dead_volume, dest="Waste_4")

#Dry and warm up the peptide
dry("Reactor_2", wait_time_dry_peptide)

c.logger.info("Ready for peptide collection. Don't forget to put a vessel under the filter2 to collect the melting water.")
#c.breakpoint() # peptide should be kept cold until next step.

c.chiller.set_temp("Reactor_2", room_temperature)
c.chiller.wait_for_temp("Reactor_2")

c.logger.info("Remove ice from filter2 and get your peptide.")
#c.breakpoint() 


########################################################################################################################
#                                                                                                                      #
#       PEPTIDE COLLECTION for freeze-drying                                                                           #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################
c.logger.info("Peptide collection for freeze-drying.")

#Clean the backbone with ACN and water as appropriate.
for i in range (3):
	c.move("ACN", "Waste_3", 10, speed=default_speed_very_fast)
	total_volume_MeCN += 10
	c.move("H2O", "Waste_6", 10, speed=default_speed_very_fast)
	total_volume_H2O += 10

#ideally would add a H2O/MeCN mixture, not separate reagents, the dissolution is performed three times, maybe the solvent volumes can be decreased?

for i in range(2): #It is important that the peptide is first treated with ACN and then with water to prevent aggregation, for freeze-drying the ratio of 2 mL ACN to 5 mL water is at the upper limit (re amount of ACN) for freeze drying -> it bubbles slightly
	
	# Add ACN to filter
	c.move("ACN", "Waste_6", priming_volume_default, speed=default_speed_fast)
	c.move("ACN", "Reactor_2", volume_dissolve_peptide_MeCN , speed=default_speed_fast, dest_port="top")
	total_volume_MeCN += priming_volume_default + volume_dissolve_peptide_MeCN

	# Add H2O to filter
	c.move("H2O", "Waste_4", priming_volume_default, speed=default_speed_fast)
	c.move("H2O", "Reactor_2", volume_dissolve_peptide_H2O, speed=default_speed_fast, dest_port="top")
	total_volume_H2O += priming_volume_default + volume_dissolve_peptide_H2O

	# Stir
	c.stirrer.set_stir_rate("Reactor_2", stirring_rate_default)
	c.stirrer.stir("Reactor_2")

	if i == 1:
		c.wait(300) # wait for 5 min to dissolve
	else:
		c.wait(30) # wait for 30 s only as the bulk of peptide already dissolved

	c.stirrer.stop_stir("Reactor_2")

	#Collect
	c.move("Reactor_2", "Product", 2 * (volume_dissolve_peptide_H2O + volume_dissolve_peptide_MeCN), speed=default_speed_very_slow)
	c.move("Reactor_2", "Product", 30, speed=default_speed_fast)

c.chiller.stop_chiller("Reactor_2")


########################################################################################################################
#                                                                                                                      #
#       FINAL BACKBONE CLEANING                                                                                        #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################
c.logger.info("Final backbone cleaning.")

clean_aq(10, 3)

# clean org with ether
for i in range(3):    
	c.move("Ether", "Waste_1", 10, speed=default_speed_fast)
	total_volume_ether +=  10 

clean_org(10, 3)

########################################################################################################################
#                                                                                                                      #
#       STOCK VOLUMES NEEDED (minimum)                                                                                 #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################
print_table()
c.logger.info("Synthesis completed!")