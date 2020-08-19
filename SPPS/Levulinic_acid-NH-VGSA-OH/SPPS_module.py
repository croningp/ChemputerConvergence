from os import path
import os

import ChemputerAPI
import SerialLabware
import sys
import string
import time as t
import datetime as dt
import copy

from chempiler import Chempiler

class  General_Params():
    def __init__(self, param_file="___SPPS_Parameter_File___.txt"):
        self.drying_times = {}
        self.sys_const = {}
        self.cleaning = {}
        self.draining = {}
        with open(param_file) as f:
            for line in f:
                if "_sequence_" in line:
                    self.peptide = f.readline().split()[0].split("-")
                elif "_scale_" in line:
                    self.scale = float(f.readline().split()[2])
                elif "_files_" in line: 
                    self.experiment_name = f.readline().split()[2]
                    self.graph_file = f.readline().split()[2]
                elif "_draining_" in line:
                    for i in range(2):
                        draining_params = []
                        reactor = f.readline().split()[2]
                        draining_params.append(float(f.readline().split()[2]))
                        draining_params.append(float(f.readline().split()[2]))
                        self.draining[reactor] = draining_params
                elif "_dry_" in line: 
                    line = f.readline().split()
                    while line:
                        self.drying_times[line[0]] = float(line[2])
                        line = f.readline().split()
                elif "_general_" in line:
                    line = f.readline().split()
                    while line:
                        self.sys_const[line[0]] = float(line[2])
                        line = f.readline().split()
                else:
                    pass
    
class Synt_Params():
    # explicit parameters for the high-level steps in the SPPS: swelling, deprotectino, coupling, washing
    def __init__(self, search_key, param_file="___SPPS_Parameter_File___.txt"):
        """
        Recieves a dictionary of reagents : volumes and two lists of times and temperatures. 
        The first time-value in times defines for how long the first temperature-value in temps has to be applied.
        Each function will run through the whole process list. 
        """
        self.reagents = []
        self.volumes = []
        self.times = []
        self.temps = []
        # reading form the parameter file
        with open(param_file) as f: 
            while True: 
                line = f.readline()                         # searching for the relevant block of parameters
                if search_key in line:
                    break
                if not line:
                    raise EOFError("No parameter block '{}' was found in the parameter file.".format(search_key))
            line = f.readline().split()
            while not "Process" in line[0]:                 # updating the list of reagents and volumes
                self.reagents.append(line[0])
                self.volumes.append(float(line[2]))
                line = f.readline().split()

            line = f.readline().split()
            while line and not("reps" in line):             # updating the list of temperatures and times
                self.temps.append(int(line[0]))
                self.times.append(int(line[2]))
                line = f.readline().split()

            if line:                                        # deciding how many repetitions are required
                self.reps = int(line[2])
            else:
                self.reps = 1
    
        self.reagent_list = [self.reagents, self.volumes]   # constructing the reagent and process lists      
        self.process_list = [self.temps, self.times]

class SPPS(General_Params): 
    reagent_stock={}
    def __init__(self):
        super().__init__()
        # get the pathes right
        self.root = path.abspath(path.dirname(__file__))
        self.output_dir = path.join(self.root, 'logs')
        self.graph_dir = path.join(self.root, self.graph_file)
        self.heater_logs_pwd = path.join(self.output_dir, 'heater_logs.txt')
        self.simulation = True
        with open(self.heater_logs_pwd, 'a') as heater_logs: 
            heater_logs.write("Data of the heating module for experiment " + self.experiment_name + ".\nThe data format is: \n")
            heater_logs.write("Time" + ' | ' + "Jacket Temperature" + ' | ' + "Temperature from Sensor 2" + ' | ' + "PWM Level" + ' | ' + "Target Temperature" + '\n')
        # create chempiler opject
        self.c = Chempiler(self.experiment_name, self.graph_dir, self.output_dir, simulation=self.simulation, device_modules=[ChemputerAPI, SerialLabware])
        self.c_calls_counter = 0

    def parse(self):
        self.log_dir = path.join(self.output_dir, "log_files")
        original_log_file = path.join(self.log_dir, self.experiment_name + ".txt")
        distilled_log_file = path.join(self.log_dir, self.experiment_name + "_distilled_log.txt")

        with open(distilled_log_file, "w") as dist: 
            with open(original_log_file) as orig: 
                line = orig.readable()
                while line: 
                    line = orig.readline()
                    if "SPPS_module" in line:
                        dist.writelines( line[line.rfind(';')+1:]) 
            dist.writelines("\nReagents neede\n")
            for i in self.reagent_stock: 
                dist.writelines(str(i) + ": " + str(self.reagent_stock[i]) + " mL\n")

        os.startfile(distilled_log_file) 

    def update_reagent_stock(self, reagent, volume): 
        """
        Takes a reagent and a volume and updates the reagent stock. 
        """
        if reagent in self.reagent_stock: 
            self.reagent_stock[reagent] += volume
        else:
            self.reagent_stock[reagent] = volume

    # general utility methods
    def clean_flask(self, volume, flask, node, solvents=("H2O_cleaning", "Ether", "Ether", "Ether")):
        """
        Empties and cleans the specified flask with the specified volume for all solvents in the solvent list. Washing solvent is put to the waste on the specified node. 

        Returns: estimated time of the process in seconds.
        """
        time = 0
        waste = "Waste_" + str(node)
        pump = "Pump_" + str(node)
        self.c.move(flask, waste, volume * 2, speed=self.sys_const["speed_fast"])
        self.c_calls_counter += 1

        for i in solvents: 
            self.c.move(i, flask, volume, speed=self.sys_const["speed_fast"])
            self.c_calls_counter += 1
            self.update_reagent_stock(i, volume)
            time += self.mix(reactor=flask, pump=pump)
            self.c.move(flask, waste, volume * 1.5, speed=self.sys_const["speed_fast"])
            self.c_calls_counter += 1
            time += volume * (3 + 1.5 * 2 ) / self.sys_const["speed_fast"] 

        return time

    def drain(self, rgnts, reactor = "Reactor_1", target="waste"):
        """
        Drains the filter frit. It removes the specified volume times the excess_factor. 
        The waiting time specifies how long the pump will pause at maximal hub to allow liquid to flow into the syringe. 

        Returns: estimated time of the process in seconds.
        """
        # WARNING: Hard-coded backbone configuration! 
        # TODO Maybe outsource that to an appropriate function - can be called from dry() as well
        
        pump = ""
        if "waste" in target.lower():
            if "_1" in reactor:
                pump = "Pump_3"
                target = "Waste_3"
            elif "_2" in reactor:
                pump = "Pump_4"
                target = "Waste_4"
        
        volume = 0
        for i in range(len(rgnts[0])): 
            volume += rgnts[1][i]

        # WARNING Hard-coded syringe size!
        moves = int(self.draining[reactor][0]*volume//10+1)
        time = 0
        for i in range(moves):
            if pump:                     
                self.c.move(reactor, pump, 10, speed=self.sys_const["speed"])
                self.c_calls_counter += 1
                self.c.wait(self.draining[reactor][1])
                self.c_calls_counter += 1
                self.c.move(pump, target, 10, speed=self.sys_const["speed_fast"])
                self.c_calls_counter += 1
                time += 10/self.sys_const["speed"]*60 + 10/self.sys_const["speed_fast"]*60 + self.draining[reactor][1] + 3
            else: 
                self.c.move(reactor, target, 10, speed=self.sys_const["speed"])
                self.c_calls_counter += 1
                time += 10/self.sys_const["speed"]*60*2
        self.c.logger.info("\tDrained {} mL with {} moves from {} to {} in ca {}".format(volume, moves, reactor, target, dt.timedelta(seconds=round(time))))
        return time

    def dry(self, *args):
        """
        Connects the filter to vacuum supply for the specified time.

        Returns: estimated time of the process in seconds.
        """
        # WARNING: Hard-coded backbone configuration!
        if "_1" in args[0]:
            pump = "Pump_3"
            vacuum = "Vacuum_1"
        elif "_2" in args[0]:
            pump = "Pump_4"
            vacuum = "Vacuum_2"
        else:
            raise ValueError("No valid reactor specification was obtained: {}.".format(reactor))

        self.c.connect(args[0], vacuum)
        self.c_calls_counter += 1
        self.c.wait(self.drying_times[args[1]])
        self.c_calls_counter += 1
        self.c.connect(args[0], pump)
        self.c_calls_counter += 1
        self.c.wait(1)  # avoids 'Actuation Failure' if the function is called twice in a row. 
        self.c_calls_counter += 1
        self.c.logger.info("Dried {} for {}.".format(args[0], dt.timedelta(seconds=round(self.drying_times[args[1]]))))
        return self.drying_times[args[1]] + 3 # Add one second per compiler call

    def reagent_handling(self, rgnts, target="Reactor_1", speed=None, priming_target=None):
        """
        Adds all reagents to target. Does not do specialised things like tube priming and air pushing. 

        Returns: estimated time of the process in seconds. 
        """
        # Only reactors require the specification of where to add the chemicals - from the top or the bottom. 
        # This function only adds chemicals to the top. 
        # Filling the bottom part of the reactor is a relativleyl specific task and must be handled in the calling function. 
        if speed is None:
            speed = self.sys_const["speed_fast"]
        
        if "Reactor" in target:
            port = "top"
        else:
            port = ""
        
        time = 0
        # adding all the reagents in the reagent list rgnts
        for i in range(len(rgnts[0])):
            if priming_target:
                self.c.move(rgnts[0][i], priming_target, self.sys_const["priming_vol"], dest_port="", speed=speed)
                self.c_calls_counter += 1 
                self.update_reagent_stock(rgnts[0][i], self.sys_const["priming_vol"])
                time += (self.sys_const["priming_vol"] / speed * 60 + 1) * 5
                self.c.logger.info("\tPrimed tubing to {} with {} mL of {}.".format(priming_target, self.sys_const["priming_vol"], rgnts[0][i]))
            self.c.move(rgnts[0][i], target, rgnts[1][i], dest_port=port, speed=speed)
            self.c_calls_counter += 1
            self.update_reagent_stock(rgnts[0][i], rgnts[1][i])
            self.c.logger.info("\tAdded {} mL of {} to {}.".format(rgnts[1][i], rgnts[0][i], target))
            time += (rgnts[1][i] / speed * 60 + 1) * 5 
        self.c.logger.info("\t\tReagents added in ca {}.".format(dt.timedelta(seconds=round(time))))
        return time

    def process_handling(self, prcs, target="Reactor_1"):
        """
        Handels the heating, stirring and time keeping for reactions, i.e. 
        it re-directs the task to the appropriate function based on which reactor is concerned. 
        
        Returns: estimated time of the process in seconds.
        """
        self.c.camera.change_recording_speed(100)
        self.c_calls_counter += 1
        if "Reactor_1" in target: 
            time = self.process_handling_1(prcs)
        elif "Reactor_2" in target: 
            time = self.process_handling_2(prcs)
        else:
            raise ValueError("No valid reactor specification was obtained.")
        self.c.camera.change_recording_speed(20)
        self.c_calls_counter += 1
        self.c.logger.info("\tPerformed the reaction in {} for {}.".format(target, dt.timedelta(seconds=round(time))))
        return time

    def process_handling_1(self, prcs):
        """
        Handels the heating, stirring and time keeping for reactions in the SPPS reactor 'Reactor_1'. 

        Returns: estimated time of the process in seconds. 
        """
        time = 0
        start = now = t.time()
        self.c.connect("Reactor_1", "Argon")
        self.c_calls_counter += 1
        self.c['Heating_Pad'].set_temp(25)                           # Set the heating temperature to a safe value
        self.c_calls_counter += 1
        self.c['Heating_Pad'].start()                                # Start heating - that engages the loop on the arduino and if your lab is baltic it will bring the heating pad to a normal temperature... 
        self.c_calls_counter += 1
        with open(self.heater_logs_pwd, 'a') as data: 
            for i in range(len(prcs[0])):                               # iterat throught the process specs
                set_tmp = self.c['Heating_Pad'].set_temp(prcs[0][i])           # set the target temp
                time += 1
                while (prcs[1][i] > (now - start)) and not self.simulation:            # then write the stats from the heating pad to the file until the waiting time is over. 
                    now = t.time()
                    data.write(str(now - start) + ' ' + str(float(self.c['Heating_Pad'].get_is_temp())) + ' ' + str(float(self.c['Heating_Pad'].get_temp(2))) + ' ' + str(int(self.c['Heating_Pad'].get_pwm())) + ' ' + str(set_tmp) + '\n')
            time +=  prcs[1][i]
        self.c['Heating_Pad'].stop()
        self.c_calls_counter += 1
        self.c.connect("Reactor_1", "Pump_3")
        self.c_calls_counter += 1
        self.c.wait(1)  # wait a second to avoid acentuation failure
        self.c_calls_counter += 1
        return time + 6           

    def process_handling_2(self, prcs):
        """
        Handels the heating, stirring and time keeping for reactions in the jacketed filter reactor 'Reactor_2'. 

        Returns: estimated time of the process in seconds. 
        """
        time = 0
        self.c.stirrer.set_stir_rate("Reactor_2", self.sys_const["stir_rate"])
        self.c_calls_counter += 1
        self.c.stirrer.stir("Reactor_2")
        self.c_calls_counter += 1
        time += 2
        for i in range(len(prcs[0])):
            self.c.chiller.set_temp("Reactor_2", prcs[0][i]) 
            self.c_calls_counter += 1
            self.c.chiller.start_chiller("Reactor_2")
            self.c_calls_counter += 1
            self.c.chiller.wait_for_temp("Reactor_2")
            self.c_calls_counter += 1
            self.c.wait(prcs[1][i])
            self.c_calls_counter += 1
            time += prcs[1][i] + 3
        self.c.stirrer.stop_stir("Reactor_2")
        self.c_calls_counter += 1
        self.c.chiller.stop_chiller("Reactor_2")
        self.c_calls_counter += 1
        return time

    def generic_reaction(self, p, *args, reactor="Reactor_1", additional_action=None, opt_p=None, drain_to="waste", priming_target=None): 
        """
        Adds all reagents, then stirs, heats, waits and finally drains.  

        Returns: estimated time of the process in seconds. 
        """
        #I don't like the implementation of the callback yet. There must be a better way to do things. 
        time = 0
        
        for i in range(p.reps):
            time += self.reagent_handling(p.reagent_list, target=reactor, priming_target=priming_target)
            time += self.process_handling(p.process_list, target=reactor)
            time += self.drain(p.reagent_list, reactor=reactor, target=drain_to)

            if additional_action:
                time += additional_action(*args)

        return time 

    def bb_cleaning(self, source = "DMF_cleaning", via = "", target = "Waste_7", reps = 2, volume = None): 
        """
        Moves specified amount of cleaing solvent to 'target' via 'via'. 
        If 'via' is an empty string, the solvent is moved directly to the target. 
        The volume of solvent used is specified in the parameter file under '_general_'.   

        Returns: estimated time of the process in seconds [volume/speed_fast*8].
        """
        time = 0
        if not volume: volume = self.sys_const["bb_cleaning_vol"] 
        move_time = (volume / self.sys_const["speed_fast"] * 60 + 1) * 8                  # estimate of how long it take to move through the hole bb once 

        for i in range(reps): 
            if via: 
                self.c.move(source, via, volume, speed=self.sys_const["speed_fast"])
                self.c_calls_counter += 1
                self.c.move(via, target, volume, speed=self.sys_const["speed_fast"])
                self.c_calls_counter += 1
                time += move_time / 8 * 12
            else: 
                self.c.move(source, target, volume, speed=self.sys_const["speed_fast"])
                self.c_calls_counter += 1
                time += move_time
            self.update_reagent_stock(source, volume)
        self.c.logger.info(" ")
        self.c.logger.info("Cleaned the back bone with {} towards {} via {} in ca {}.".format(source, target, via, dt.timedelta(seconds=round(time))))
        return time 

    def mix(self, reactor="Cleavage_mix", pump="Pump_7", reps = 3): 
        """
        Mixes the content in the reactor by aspiring it to the the specified pump.   

        Returns: estimated time of the process in seconds [].
        """
        for i in range(reps):                    
            self.c.move(reactor, pump, 10, speed=self.sys_const["speed"])
            self.c_calls_counter += 1
            self.c.wait(1)
            self.c_calls_counter += 1
            self.c.move(pump, reactor, 10, speed=self.sys_const["speed"])
            self.c_calls_counter += 1

        time = (20.0 / self.sys_const["speed"] + 1 + 3) * reps   
        self.c.logger.info("Mixed {} for ca {}.".format(reactor, dt.timedelta(seconds=round(time))))
        return time

    # top-level methods
    def cleavage(self, target = "Reactor_2", port = "top", reactor = "Reactor_1"): 
        """
        Performs the cleavage of the peptide product and delivers it to the target vessel.   

        Returns: estimated time of the process in seconds [].
        """
        self.c.logger.info(" ")
        self.c.logger.info("Cleavage")
        time = 0
        if not "Reactor" in target: 
            port = ""

        #Prepare the cleavage cocktail
        p = Synt_Params("_cleavage_mix_")
        time += self.reagent_handling(p.reagent_list, target="Cleavage_mix", speed=self.sys_const["speed_slow"], priming_target="Waste_7")
        time += self.mix("Cleavage_mix")

        #Perform the actual cleavage 
        cleavage = [Synt_Params("_cleavage_1_"), Synt_Params("_cleavage_2_")]
        for i in cleavage:
            time += self.generic_reaction(i, drain_to=target)

        time += self.bb_cleaning(source="H2O_cleaning", via="Pump_7", target="Waste_3", volume = self.sys_const["bb_cleaning_vol_large"])
        time += self.bb_cleaning(source="Ether", via="Pump_7", target="Waste_3", volume = self.sys_const["bb_cleaning_vol_large"])

        return time

    def cleave_and_precipitate(self, reactor = "Reactor_2", drain_to="waste"): 
        """
        Performs the cleavage and precipitation of the peptide product.   

        Returns: estimated time of the process in seconds [].
        """
        self.c.logger.info(" ")
        self.c.logger.info("Cleavage and Precipitation")
        time = 0 
        prcp = Synt_Params("_precipitate_")  

        # Getting the reactor ready for the precipitation
        self.c.chiller.set_temp(reactor, prcp.process_list[0][0]) # This is a bit hacky, sorry. First the reactor 2 is filled with ether and chilled down to avoid a waiting between cleavage and precipitation. 
        self.c_calls_counter += 1
        self.c.chiller.start_chiller(reactor)
        self.c_calls_counter += 1
        self.c.stirrer.set_stir_rate(reactor, self.sys_const["stir_rate"])
        self.c_calls_counter += 1
        self.c.stirrer.stir(reactor)
        self.c_calls_counter += 1
        time += 4
        time += self.reagent_handling(prcp.reagent_list, target=reactor)    # TODO filling the bottom of Reactor 2
        
        # Perform the cleavage and percipitation
        time += self.cleavage() 
        self.c.chiller.wait_for_temp(reactor) # There is a small chance that by the time the cleavage is done, the target temperature in reactor is not reached
        self.c_calls_counter += 1
        time += self.process_handling(prcp.process_list, target=reactor)
        time += self.drain(prcp.reagent_list, reactor="Reactor_2", target=drain_to)
        
        # Perform the washing of the precipitate
        time += self.generic_reaction(Synt_Params("_precipitate_wash_"), reactor, "precipitate_short_drying", reactor=reactor, additional_action=self.dry) #TODO check in how far that corresponds to the original washing procedure. 
        time += self.dry("Reactor_2", "precipitate_long_drying")

        return time

    def collection(self, p=Synt_Params("_collection_"), reactor = "Reactor_2", product = "Product"): 
        """
        Collects the final product and delivers it to the target vial.    

        Returns: estimated time of the process in seconds [].
        """
        self.c.logger.info(" ")
        self.c.logger.info("Collection")
       
        # Warming the precipitate up to target temperature
        self.c.chiller.set_temp(reactor, p.process_list[0][0])
        self.c_calls_counter += 1
        self.c.chiller.start_chiller(reactor)
        self.c_calls_counter += 1
        self.c.chiller.wait_for_temp(reactor)
        self.c_calls_counter += 1
        time = 2
        
        # Cleaning the backbone properly once more
        time += self.bb_cleaning(source="ACN", target="Waste_3", volume=self.sys_const["bb_cleaning_vol_large"])
        time += self.bb_cleaning(source="H2O", target="Waste_3", volume=self.sys_const["bb_cleaning_vol_large"])
        time += self.generic_reaction(p, reactor=reactor, drain_to=product, priming_target="Waste_4")
        self.c.logger.info("Collected the product in {} with {} and placed it in {} in ca {}.".format(reactor, p.reagent_list, product, dt.timedelta(seconds=round(time))))
        
        return time

    def deprotection(self): 
        """
        Perfroms the Fmoc-deprotection.    

        Returns: estimated time of the process in seconds [].
        """
        #TODO make the function more flexilbe - at the moment double-deprotection is hard-coded as is the paramter key '_parameter_key_'
        time = 0
        self.c.logger.info(" ")
        self.c.logger.info("Deprotection stage 1")
        time += self.generic_reaction(Synt_Params("_deprotection_1_"), priming_target="Waste_3")
        time += self.bb_cleaning(target="Waste_5")
        self.c.logger.info(" ")
        self.c.logger.info("Deprotection stage 2")
        time += self.generic_reaction(Synt_Params("_deprotection_2_"), priming_target="Waste_3")
        time += self.bb_cleaning(target="Waste_5")
        self.c.logger.info(" ")
        self.c.logger.info("Wash after deprotection")
        time += self.generic_reaction(Synt_Params("_wash_"))

        return time

    def coupling(self, aa, parameters="_coupling_"): 
        """
        Perfroms HBTU coupling.    

        Returns: estimated time of the process in seconds [].
        """
        time = 0
        coupling = Synt_Params(parameters)

        for n, i in enumerate(coupling.reagent_list[0]):
            if 'AminoAcid' in i:
                coupling.reagent_list[0][n] = aa    

        reps = coupling.reps
        coupling.reps = 1
 
        for i in range(reps): 
            self.c.logger.info(" ")
            self.c.logger.info("Coupling of amino acid '{}'".format(aa))
            time += self.generic_reaction(coupling, priming_target="Waste_3")
            self.c.logger.info(" ")
            self.c.logger.info("Wash after coupling")
            time += self.generic_reaction(Synt_Params("_wash_")) 
            time += self.bb_cleaning(source="DMF", target="Waste_2_1", via="Pump_3") 

        return time

    def synthesis(self):
        """
        Orchestrates the whole process of synthesising the peptide as specified in the paramter file. 

        Returns: estimated time of the process in seconds [].
        """
        wall_time_start = t.time()
        time = self.bb_cleaning(volume=self.sys_const["bb_cleaning_vol_large"])

        #Start Video Log
        self.c.start_recording() 
        self.c_calls_counter += 1
        self.c.camera.change_recording_speed(20)
        self.c_calls_counter += 1
        
        #Swelling
        self.c.logger.info(" ")
        self.c.logger.info("Swelling the resin")
        time += self.generic_reaction(Synt_Params("_swell_resin_"), priming_target="Waste_3")

        for aa in reversed(self.peptide):
            #Deprotection & Washing
            time += self.deprotection()
            #Coupling & Washing
            time += self.coupling(aa)
           
        #Final Deprotection
        #time += self.deprotection()

        #Final Washing (includes the backbone)
        time += self.bb_cleaning(volume=self.sys_const["bb_cleaning_vol_large"])
        time += self.bb_cleaning(source="Ether", target="Waste_3", via="Pump_7", volume=self.sys_const["bb_cleaning_vol_large"])
        time += self.bb_cleaning(source="DCM", target="Waste_3", via="Pump_7", volume=self.sys_const["bb_cleaning_vol_large"])
        self.c.logger.info(" ")
        self.c.logger.info("Final wash with DCM")
        time += self.generic_reaction(Synt_Params("_DCM_wash_"))
        time += self.dry("Reactor_1", "final_SPPS_drying")
        self.c.logger.info(" ")
        self.c.logger.info("Peptide synthesis is done after ca {}.".format(dt.timedelta(seconds=round(time))))
        
        #Cleavage, Precipitation and Washing
        time += self.cleave_and_precipitate()
        self.c.logger.info(" ")
        self.c.logger.info("Cleavage and precipitation is done after ca {}.".format(dt.timedelta(seconds=round(time))))
        
        #Collection of Product
        time += self.collection()
        self.c.logger.info(" ")
        self.c.logger.info("Product collection is done after ca {}.".format(dt.timedelta(seconds=round(time))))
        self.c.logger.info("Estimated time: {}, Actual duration: {}.".format(dt.timedelta(seconds=round(time)), dt.timedelta(seconds=round(t.time() - wall_time_start))))
        
        #Distill important info out of the log file
        self.parse()

        #Stop video log
        self.c.camera.stop()
        self.c_calls_counter += 1

        if self.simulation:
            return time 
        else:
            return t.time() - wall_time_start

if __name__ == '__main__': 
    spps = SPPS()
    print("Synthesis time: {}.\n".format(dt.timedelta(seconds=round(spps.synthesis()))))
    print("Number of chempiler calls: {}.".format(spps.c_calls_counter))
    clean_all_my_flasks = False
    if clean_all_my_flasks:
        spps.clean_flask(30, "Cleavage_mix", 7)
        spps.clean_flask(30, "Ser", 1, solvents=("MeOH", "MeOH", "DMF_cleaning"))
        spps.clean_flask(30, "Val", 1, solvents=("MeOH", "MeOH", "DMF_cleaning"))
        spps.clean_flask(30, "Gly", 1, solvents=("MeOH", "MeOH", "DMF_cleaning"))
        spps.clean_flask(30, "Lev", 2, solvents=("MeOH", "MeOH", "DMF_cleaning"))
        spps.clean_flask(50, "HBTU", 2, solvents=("MeOH", "MeOH", "MeOH"))
   

