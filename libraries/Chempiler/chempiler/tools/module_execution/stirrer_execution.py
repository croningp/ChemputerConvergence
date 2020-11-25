"""
(c) 2019 The Cronin Group, University of Glasgow

This class provides all real-life applications of hotplate stirrers within the
Chemputer rig, essentially
just wrapping the original class methods.
"""

import logging
from time import sleep

from chempiler.tools.constants import COOLING_THRESHOLD


class StirrerExecutioner(object):
    """
    Class to interface with Stirrer plates

    TODO: add try/except statements to catch calls to unsupported methods!
    """
    def __init__(self, graph, simulation):
        """
        Initialiser for the StirrerExecutioner class

        Args:
            graph (DiGraph): Graph representing the platform
            simulation (bool): Simulation mode
        """
        self.graph = graph
        self.simulation = simulation
        self.logger = logging.getLogger(
            "main_logger.stirrer_executioner_logger")

    def _get_stirrer_object(self, node_name):
        """
        Iterates over the graph and looks for the stirrer attached to the node
        passed as argument.
        NOTA BENE: If more than one stirrer is attached to one node, one of them
        is returned, with no guarantee which one.

        Args:
            node_name (str): Name of a node in the graph

        Returns:
            SerialLabware object representing the stirrer attached to the node.

        Raises:
            KeyError: An error if no stirrer is found.
        """
        if node_name in self.graph.nodes():
            for attached_node in self.graph.predecessors(node_name):
                node_object = self.graph.obj(attached_node)
                # use duck-typing to decide if `node_object` is a stirrer
                if hasattr(node_object, "start_stirrer"):
                    return node_object
            raise KeyError(
                "ERROR: node {0} has no recognised stirrer attached!".format(
                    node_name))
        else:
            raise KeyError("ERROR: node {0} is not recognised!".format(
                node_name))

    def _get_heater_object(self, node_name):
        """
        Iterates over the graph and looks for the heater attached to the node
        passed as argument. NOTA BENE: If more than one heater is attached to
        one node, one of them is returned, with no guarantee which one.

        Args:
            node_name (str): Name of a node in the graph

        Returns:
            SerialLabware object representing the heater attached to the node.

        Raises:
            KeyError: An error if no heater is found.
        """
        if node_name in self.graph.nodes():
            for attached_node in self.graph.predecessors(node_name):
                node_object = self.graph.obj(attached_node)
                # use duck-typing to decide if `node_object` is a heater
                if hasattr(node_object, "start_heater"):
                    return node_object
            raise KeyError(
                "ERROR: node {0} has no recognised heater attached!".format(
                    node_name))
        else:
            raise KeyError(
                "ERROR: node {0} is not recognised!".format(node_name))

    def stir(self, node_name):
        """
        Starts the stirring the stirrer plate

        Args:
            node_name (str): Name of the stirrer
        """
        self.logger.info(
            "Starting stirring for hotplate {0}...".format(node_name))
        stirrer_obj = self._get_stirrer_object(node_name)
        stirrer_obj.start_stirrer()
        self.logger.info("Done.")

    def heat(self, node_name):
        """
        Starts heating the stirrer plate

        Args:
            node_name (str): Name of the stirrer
        """
        self.logger.info(
            "Starting heating for hotplate {0}...".format(node_name))
        heater_obj = self._get_heater_object(node_name)
        heater_obj.start_heater()
        self.logger.info("Done.")

    def wait_for_temp(self, node_name):
        """
        Waits for the stirrer to reach its setpoint temperature (approaching
        from either way)

        Args:
            node_name (str): Name of the stirrer
        """
        if self.simulation:
            self.logger.info("Waiting for temperature... Done.")
        else:
            heater_obj = self._get_heater_object(node_name)
            while True:
                try:
                    setpointfloat = float(heater_obj.temperature_sp[0])
                    start_temp = float(heater_obj.temperature_pv[0])
                    break
                except Exception:
                    continue
            self.logger.info(
                "Heater {0} waiting to reach {1}°C...".format(
                    node_name, setpointfloat))
            if start_temp < setpointfloat:  # approach from below
                while True:
                    try:
                        current_temp = float(heater_obj.temperature_pv[0])
                        if current_temp > (setpointfloat - COOLING_THRESHOLD):
                            break
                        else:
                            self.logger.info(
                                "Still heating... Current temperature:\
 {0}°C".format(current_temp))
                            sleep(5)
                    except Exception:
                        continue
            elif start_temp > setpointfloat:  # approach from above
                while True:
                    try:
                        current_temp = float(heater_obj.temperature_pv[0])
                        if current_temp < (setpointfloat + COOLING_THRESHOLD):
                            break
                        else:
                            self.logger.info(
                                "Still cooling... Current temperature:\
 {0}°C".format(current_temp))
                            sleep(5)
                    except Exception:
                        continue

    def stop_stir(self, node_name):
        """
        Stops stirring the stirrer plate

        Args:
            node_name (str): Name of the stirrer
        """
        self.logger.info(
            "Stopping stirring for hotplate {0}...".format(node_name))
        stirrer_obj = self._get_stirrer_object(node_name)
        stirrer_obj.stop_stirrer()
        self.logger.info("Done.")

    def stop_heat(self, node_name):
        """
        Stops heating the stirrer plate

        Args:
            node_name (str): Name of the stirrer
        """
        self.logger.info(
            "Stopping heating for hotplate {0}...".format(node_name))
        heater_obj = self._get_heater_object(node_name)
        heater_obj.stop_heater()
        self.logger.info("Done.")

    def set_temp(self, node_name, temp):
        """
        Sets the temperature of the stirrer plate

        Args:
            node_name (str): Name of the stirrer
            temp (float): Temperature to set
        """
        self.logger.info(
            "Setting temperature for hotplate {0} to {1}°C...".format(
                node_name, temp))
        heater_obj = self._get_heater_object(node_name)
        heater_obj.temperature_sp = temp
        self.logger.info("Done.")

    def set_stir_rate(self, node_name, stir_rate):
        """
        Sets the stirring rate of the stirrer

        Args:
            node_name (str): Name of the stirrer
            stir_rate (int): Stirring rate to set
        """
        self.logger.info(
            "Setting stir rate for hotplate {0} to {1} RPM...".format(
                node_name, stir_rate))
        stirrer_obj = self._get_stirrer_object(node_name)
        stirrer_obj.stir_rate_sp = stir_rate
        self.logger.info("Done.")
