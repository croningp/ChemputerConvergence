"""
(c) 2019 The Cronin Group, University of Glasgow

This class provides all real-life applications of recirculation chillers within
the Chemputer rig, essentially just wrapping the original class methods.
"""

import logging
from time import sleep

from chempiler.tools.constants import COOLING_THRESHOLD


class ChillerExecutioner(object):
    """
    Class for interfacing with the Chiller objects
    """
    def __init__(self, graph, simulation):
        """
        Initialiser for the ChillerExecutioner class

        Args:
            graph (DiGraph): Graph representing the platform
            simulation (bool): Simulation mode
        """
        self.graph = graph
        self.simulation = simulation
        self.logger = logging.getLogger(
            "main_logger.chiller_executioner_logger")

    def _get_chiller_object(self, node_name):
        """
        Iterates over the graph and looks for the chiller attached to the node
        passed as argument. NOTA BENE: If more than one chiller is attached to
        one node, one of them is returned, with no guarantee which one.

        Args:
            node_name (str): Name of a node in the graph

        Returns:
            SerialDevice: SerialLabware object representing the chiller attached
                          to the node.

        Raises:
            KeyError: An error if no chiller is found.
        """

        if node_name in self.graph.nodes:
            for node in self.graph.predecessors(node_name):
                node_object = self.graph.obj(node)
                if hasattr(node_object, "start"):
                    return node_object
            raise KeyError(
                "ERROR: node {0} has no recognised chiller attached!".format(
                    node_name))
        else:
            raise KeyError(
                "ERROR: node {0} is not recognised!".format(node_name))

    def start_chiller(self, node_name):
        """
        Starts the circulation and heating/cooling action

        Args:
            node_name (str): Name of the chiller
        """
        self.logger.info("Starting chiller {0}...".format(node_name))
        chiller_obj = self._get_chiller_object(node_name)
        chiller_obj.start()
        self.logger.info("Done.")

    def stop_chiller(self, node_name):
        """
        Stops the circulation and heating/cooling action

        Args:
            node_name (str): Name of the chiller
        """
        self.logger.info("Stopping chiller {0}...".format(node_name))
        chiller_obj = self._get_chiller_object(node_name)
        chiller_obj.stop()
        self.logger.info("Done.")

    def set_temp(self, node_name, temp):
        """
        Sets the temperature of the chiller

        Args:
            node_name (str): Name of the chiller
            temp (float): Temperature to set
        """
        self.logger.info(
            "Setting temperature for chiller {0} to {1}°C...".format(
                node_name, temp))
        chiller_obj = self._get_chiller_object(node_name)
        chiller_obj.set_temperature(temp=temp)
        self.logger.info("Done.")

    def cooling_power(self, node_name, cooling_power):  # TODO check if CF41
        """
        Sets the cooling power of the chiller. Only works with Julabo CF41.

        Args:
            node_name (str): Name of the chiller
            cooling_power (int): Cooling power in % (range 0..100)
        """
        self.logger.info(
            "Setting cooling power for chiller {0} to {1}%...".format(
                node_name, cooling_power))
        chiller_obj = self._get_chiller_object(node_name)
        chiller_obj.set_cooling_power(cooling_power=cooling_power)
        self.logger.info("Done.")

    # This doesn't work for all chillers
    def ramp_chiller(self, node_name, ramp_duration, temp):
        """
        Sets the ramp duration and the end temperature for the chiller

        Args:
            node_name (str): Name of the chiller
            ramp_duration (int): Duration of the ramp in sec
            temp (float): End temperature to ramp to in °C
        """
        self.logger.warning(f"This may fail depending on your type of Chiller!")
        self.logger.info(
            "Chiller {0}: Setting ramp duration to {1}s and temperature to\
 {2}°C...".format(node_name, ramp_duration, temp))
        chiller_obj = self._get_chiller_object(node_name)
        chiller_obj.set_ramp_duration(ramp_duration=ramp_duration)
        chiller_obj.start_ramp(temp=temp)
        self.logger.info("Done.")

    def wait_for_temp(self, node_name):
        """
        Waits for the chiller to reach its setpoint temperature (approaching
        from either way)

        Args:
            node_name (str): Name of the chiller
        """
        if self.simulation:
            self.logger.info("Waiting for temperature... Done.")
        else:
            chiller_obj = self._get_chiller_object(node_name)
            setpoint = chiller_obj.get_setpoint()
            self.logger.info("Chiller {0} waiting to reach {1}°C...".format(
                node_name, setpoint))
            if chiller_obj.get_temperature() < setpoint:  # approach from below
                while (abs(chiller_obj.get_temperature() - setpoint)
                       > COOLING_THRESHOLD):
                    self.logger.info(
                        "Still heating... Current temperature: {0}°C".format(
                            chiller_obj.get_temperature()))
                    sleep(5)
            # approach from above
            elif chiller_obj.get_temperature() > setpoint:
                while (abs(chiller_obj.get_temperature() - setpoint)
                       > COOLING_THRESHOLD):
                    self.logger.info(
                        "Still cooling... Current temperature: {0}°C".format(
                            chiller_obj.get_temperature()))
                    sleep(5)
