"""
(c) 2019 The Cronin Group, University of Glasgow

This class provides convience methods for operating vacuum pumps within the
Chemputer rig, essentially wrapping the original class methods. It also has a
"vent to ambient pressure" function for convenience.
"""

import logging
from time import sleep

from chempiler.tools.constants import ATMOSPHERIC_PRESSURE


class VacuumExecutioner:
    """
    Class to interface with the CVC3000 vacuum pump
    """
    def __init__(self, graph, simulation):
        """
        Initialiser for the VacuumExecutioner class.

        Args:
            graph (DiGraph): Graph representing the platform
            simulation (bool): Simulation mode
        """
        self.graph = graph
        self.simulation = simulation
        self.logger = logging.getLogger("main_logger.vacuum_executioner_logger")

    def _get_vacuum_object(self, node_name):
        """
        Iterates over the graph and looks for the vacuum pump attached to the
        node passed as argument. NOTA BENE: If more than one vacuum pump is
        attached to one node, one of them is returned, with no guarantee which
        one.

        Args:
            node_name (str): Name of a node in the graph

        Returns:
            Object representing the vacuum pump attached to the node.

        Raises:
            KeyError: An error if vacuum object is not found.
        """
        if node_name in self.graph.nodes():
            for attached_node in self.graph.predecessors(node_name):
                node_object = self.graph.obj(attached_node)
                # use duck-typing to decide if `node_object` is a vacuum pump
                if hasattr(node_object, "vacuum_sp"):
                    return node_object
            raise KeyError(
                "ERROR: node {0} has no recognised vacuum attached!".format(
                    node_name))
        else:
            raise KeyError(
                "ERROR: node {0} is not recognised!".format(node_name))

    def initialise(self, node_name):
        """
        Sets up the vacuum pump, getting it ready for operation

        Args:
            node_name (str): The name of the vacuum pump
        """
        self.logger.info("Initialising vacuum pump {0}...".format(node_name))
        vacuum_obj = self._get_vacuum_object(node_name)
        vacuum_obj.initialise()
        self.logger.info("Done.")

    def get_vacuum_set_point(self, node_name):
        """
        Reads the set point (target) for the vacuum pump in Vac control

        Args:
            node_name (str): The name of the vacuum pump
        """
        vacuum_obj = self._get_vacuum_object(node_name)
        self.logger.info("Vacuum setpoint for vacuum pump {0} is {1}...".format(
            node_name, vacuum_obj.vacuum_sp))

    def set_vacuum_set_point(self, node_name, vac):
        """
        Sets the vacuum set point

        Args:
            node_name (str): The name of the vacuum pump
            vac (int): Set point to set
        """
        self.logger.info(
            "Setting vacuum for vacuum pump  {0} to {1}mbar...".format(
                node_name, vac))
        vacuum_obj = self._get_vacuum_object(node_name)
        vacuum_obj.vacuum_sp = vac
        self.logger.info("Done.")

    def start_vacuum(self, node_name):
        """
        Starts the vacuum pump

        Args:
            node_name (str): The name of the vacuum pump
        """
        self.logger.info("Starting vacuum pump {0}...".format(node_name))
        vacuum_obj = self._get_vacuum_object(node_name)
        vacuum_obj.start()
        self.logger.info("Done.")

    def stop_vacuum(self, node_name):
        """
        Stops the vacuum pump

        Args:
            node_name (str): The name of the vacuum pump
        """
        self.logger.info("Stopping vacuum pump {0}...".format(node_name))
        vacuum_obj = self._get_vacuum_object(node_name)
        vacuum_obj.stop()
        self.logger.info("Done.")

    def vent_vacuum(self, node_name):
        """
        Vents all the way to atmospheric pressure.

        Args:
            node_name (str): The name of the vacuum pump
        """
        self.logger.info("Venting vacuum pump {0}...".format(node_name))
        if self.simulation:
            self.logger.info("Pffffffffsssssshhhhhhhhhh...")
        else:
            vacuum_obj = self._get_vacuum_object(node_name)
            vacuum_obj.vent()
            # wait for the venting to complete
            while True:
                pressure = vacuum_obj.vacuum_pv()
                self.logger.debug("Current pressure is {0} {1}.".format(
                    pressure[0], pressure[1]))
                if float(pressure[0]) > ATMOSPHERIC_PRESSURE:
                    vacuum_obj.vent(0)
                    self.logger.info("Venting finished.")
                    break
                else:
                    self.logger.debug("Still venting...")
                    sleep(5)
            self.logger.info("Done.")

    def get_status(self, node_name):
        """
        Gets the status of the vacuum pump

        Args:
            node_name (str): The name of the vacuum pump
        """
        vacuum_obj = self._get_vacuum_object(node_name)
        self.logger.info(vacuum_obj.query_status())

    def get_end_vacuum_set_point(self, node_name):
        """
        Gets the set point (target) for the switch off vacuum in mode Auto

        Args:
            node_name (str): The name of the vacuum pump
        """
        vacuum_obj = self._get_vacuum_object(node_name)
        self.logger.info(vacuum_obj.end_vacuum_sp)

    def set_end_vacuum_set_point(self, node_name, vac):
        """
        Sets the switch off vacuum set point

        Args:
            node_name (str): The name of the vacuum pump
            vac (int): Set point value to set
        """
        vacuum_obj = self._get_vacuum_object(node_name)
        vacuum_obj.end_vacuum_sp = vac

    def get_runtime_set_point(self, node_name):
        """
        Gets the set point (target) for the run time in mode Auto

        Args:
            node_name (str): The name of the vacuum pump
        """
        vacuum_obj = self._get_vacuum_object(node_name)
        self.logger.info(vacuum_obj.runtime_sp)

    def set_runtime_set_point(self, node_name, time):
        """
        Sets the set point for the runtime

        Args:
            node_name (str): The name of the vacuum pump
            time (int): Desired runtime
        """
        vacuum_obj = self._get_vacuum_object(node_name)
        vacuum_obj.runtime_sp = time

    def set_speed_set_point(self, node_name, speed):
        """
        Sets the set point for the speed

        Args:
            node_name (str): The name of the vacuum pump
            speed (int): Desired speed
        """
        self.logger.info("Setting speed for vacuum pump {0} to {1}%...".format(
            node_name, speed))
        vacuum_obj = self._get_vacuum_object(node_name)
        vacuum_obj.speed_sp = speed

    def auto_evaporation(
        self,
        node_name,
        auto_mode=2,
        vacuum_limit=1,
        duration=180,
        vent_after=True
    ):
        """
        Starts an automatic determination of the boiling vacuum

        Short manual:
        ------------
        The automatic mode works correct and quite reliable for simple solvent
        mixtures and will make your evaporation routine easier. However,
        it is not ideal, especially if set up incorrectly. Below is the quick
        manual:

        1) Select the proper sensitivity mode for your mixture:
            - HIGH (auto_mode=2, Default) is generally recommended for small
                solvent quantities and will lead to longer process time
            - NORMAL (auto_mode=1) is what it says - "normal"
            - LOW (auto_mode=0) is used for "uncritical" processes to reduce
                process time
        2) Choose the appropriate minimum vacuum point, it might set to:
            - Specific value in mbar (vacuum_limit=value) and must be chosen
                with respect to your solvent boiling point at room temperature,
                otherwiseyou will face the situation when he solvent will start
                to evaporate from the collecting flask and the process will
                never finish.
            - OFF (with vacuum_limit=0) however this will definitely lead to the
                situation described above.
            - AUTO (vacuum_limit=1) - to relay on the Vacuubrand algorithms for
                the automatic end point determination, however it is only
                recommended for large amount of solvent.
        3) Set the duration limit to prevent evaporation process
        from running forever. By default it is set to 3 hours which should be
        sufficient to evaporate anything on the current Chemputer scale.
        4) If you don't want to vent you system through vacuum pump (i.e. you
           need to maintain inert athmospere) you may select not to do it with
           vent_after set to False

        Args:
            node_name (str): The name of the vacuum pump
            auto_mode (int): Sensitivity parameter for the automatic boiling
                point determination; possible values - 0: "HIGH"; 1: "NORMAL";
                2: "LOW"
            vacuum_limit (int): Minimum pressure for the process;
                possible values - 0: "OFF"; 1: "AUTO"; 2-1060: actual value in
                mbar
            duration (float): Duration limit in minutes; maximum value: 1440.0
            vent_after (bool): (Optional) If you want to vent the pump after
                evaporation finished
        """
        # obtaining the vacuum node
        self.logger.info("Starting automatic boiling vacuum determination")
        vacuum_obj = self._get_vacuum_object(node_name)

        # converting duration time to proper string
        if 0 < duration <= 1440:
            duration = int(duration)
            duration_time = f'{duration//60:02}:{duration%60:02}'
        else:
            raise ValueError(
                'Please select meaningful process time: >0 and <= 1440 minutes')

        # checking the input parameters
        if auto_mode == 0:
            auto_mode = 'auto low'
            self.logger.info(
                'You have chosen low sensitivity automatic evaporation process')
            self.logger.warning(
                'It is only recommended for "uncritical" processes')
        elif auto_mode == 1:
            auto_mode = 'auto normal'
            self.logger.info(
                'You have chosen normal sensitivity automatic evaporation\
 process')
        elif auto_mode == 2:
            auto_mode = 'auto high'
            self.logger.info(
                'You have chosen high sensitivity automatic evaporation\
 process')
            self.logger.warning('It may lead to increased process time')
        else:
            raise ValueError('The selected auto mode is not valid')

        if vacuum_limit == 0:
            self.logger.warning(
                f'Automatic evaporation process is going to run with NO minimum\
 value.\nThis might lead to solvent loss, pump degradation, explosion, cancer\
 and increased duration time up to {duration//60:02}H:{duration%60:02}M)')
        elif vacuum_limit == 1:
            self.logger.info('Automatic evaporation process is going to run\
 with AUTO minimum value')
            self.logger.warning(
                'It is only recommended for large solvent quantity')
        elif 2 <= vacuum_limit <= 1060:
            self.logger.info(
                f'Automatic evaporation process is going to run with\
 {vacuum_limit} mbar minimum value')
        else:
            raise ValueError(
                'Select appropriate minimum vacuum point, e.g. 0 for "OFF", 1\
 for "AUTO, or 2-1060 for actual mbar value')

        # setting the auto mode
        vacuum_obj.set_mode(auto_mode)

        # setting the minimum vacuum limit
        vacuum_obj.end_vacuum_sp = vacuum_limit

        # setting the maximum duration period
        self.set_runtime_set_point(node_name, duration_time)

        # starting the vacuum pump
        self.start_vacuum(node_name)

        # monitoring pressure and status
        while True:
            pressure = vacuum_obj.vacuum_pv()
            status = vacuum_obj.query_status()

            # controller state is either 0 - pump is off; 1 - pumping down;
            # 2 - boiling pressure found (plateau), 3 - current pressure is
            # below the set pressure (minimum) and the pump stops
            if not status:  # For simulations
                controller_state = 3
            else:
                controller_state = int(status['Controller state'])
            if controller_state == 0:
                self.logger.info('Pump shut down')
                break
            elif controller_state == 1:
                self.logger.info(
                    f'Pumping down, current pressure is {pressure[0]}\
 {pressure[1]}')
                sleep(5)
            elif controller_state == 2:
                self.logger.info(
                    f'Boiling plateau reached, solvent evaporating.\nCurrent\
 pressure is {pressure[0]} {pressure[1]}')
                sleep(5)
            elif controller_state == 3:
                self.logger.info('Minimum pressure reached, solvent evaporated')
                break
            else:
                self.logger.debug('Wrong controller state, should not happen')

                # if something went wrong: stop, vent and return the vacuum
                # pump to default control mode
                vacuum_obj.stop()
                vacuum_obj.vent()
                vacuum_obj.set_mode('vac control')

                raise RuntimeError(
                    'Wrong controller state returned from pump, please check\
 manually')

        # when everything is done and the vacuum pump is switched off
        # you need to stop the process and vent the whole system if required
        self.stop_vacuum(node_name)

        if vent_after:
            self.vent_vacuum(node_name)

        # setting the vac control mode and duration time back
        vacuum_obj.set_mode('vac control')
        self.set_runtime_set_point(node_name, '03:00')
