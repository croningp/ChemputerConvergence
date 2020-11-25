"""
(c) 2019 The Cronin Group, University of Glasgow

This class ties all other modules together. First, the logging module is
initialised. Then, a GraphML file is parsed into a networkx graph object
containing the architecture. Finally, the executioners for the various device
classes are then instantiated and exposed to the user.
"""

# Standard library
import logging
import os
import sys
import time
import math
import threading
import queue
import json
from typing import (
    Dict, Any, Optional, Union, List, Generator)
from types import ModuleType

# Relative imports
# Executioners
from .tools.module_execution.pump_execution import PumpExecutioner
from .tools.module_execution.stirrer_execution import StirrerExecutioner
from .tools.module_execution.vacuum_execution import VacuumExecutioner
from .tools.module_execution.chiller_execution import ChillerExecutioner
from .tools.module_execution.camera_execution import CameraExecutioner

# Video logging
from .tools.vlogging import VlogHandler, RecordingSpeedFilter, recording_worker

# Constants
from .tools.logging import get_logger
from .tools.errors import IllegalLockError

# Graph
from .tools.graph import ChempilerGraph

class Chempiler(object):
    """Chempiler master class. Handles setup and initialisation of the platform,
    then exposes the executioner modules to the user.

    Attributes:
        graph (ChempilerGraph): Graph of physical setup with all nodes
            containing an 'obj' attribute that is the instantiated device
            object for that node.
        capabilities: Iterable[Tuple[str, str, Tuple]]: Iterator over all
            possible liquid movement operations the system is capable as
            tuples (operation, node, edge).
            operation - 'sink', 'source' or 'route'
            node - name of the node involved
            edge - Tuple of edge(s) involved in operation.
                sink - (source_node, node, edge_weight)
                source - (node, sink_node, edge_weight)
                route - (
                    (source_node, node, edge_weight),
                    (node, dest_node, edge_weight)
                )
        pump (PumpExecutioner): Class exposing separate phases method.
        vacuum (VacuumExecutioner): Class exposing vacuum methods.
        stirrer (StirrerExecutioner): Class exposing stirrer/heater methods.
        chiller (ChillerExecutioner): Class exposing chiller methods.
        camera (CameraExecutioner): Class exposing camera methods.
    """
    def __init__(
        self,
        experiment_code: str,
        graph_file: Union[str, Dict[str, List[Dict[str, Any]]]],
        output_dir: str,
        simulation: bool,
        device_modules: Optional[List[ModuleType]]
    ) -> None:
        """
        Initialiser method of the Chempiler class. Initialises crash dump
        folder, logging, parses the graph and instantiates device objects for
        each node, then finally initialises executioners and exposes them as
        attributes of self.

        Args:
            exp_name (str): A unique identifier to link the output to
                other experimental documentation (lab book etc).
            graph (Union[str, Dict[str, List[Dict[str, Any]]]): Graph can
                be a path to a graphML or JSON node link graph file. It can
                also be a direct dict of a JSON node link graph.
            output_dir (str): Absolute path to directory for output files,
                e.g. logs, videos, crash dump.
            simulation (bool): Switch between simulation mode (commands are
                logged to file) and operational mode.
            device_modules (list): List of modules containing devices to be used
                in experiment, Defaults to [ChemputerAPI].
        """

        # Give parameters passed at instantiation to object.
        self.exp_name = experiment_code
        self.output_dir = output_dir
        self.simulation = simulation
        self.device_modules = device_modules or []

        # Initialise everything.
        self.initialise_logging()
        self.graph = ChempilerGraph(
            graph_file, self.logger, self.device_modules, self.simulation
        )
        self.setup_platform()
        self.initialise_crash_dump()
        self.initialise_executioners()

        # Expose Methods
        self.move = self.pump.move
        self.move_duration = self.pump.move_duration
        self.move_locks = self.pump.move_locks
        self.connect = self.pump.connect_nodes

    ##################
    # INITIALISATION #
    ##################

    def initialise_crash_dump(self) -> None:
        """
        Initialise crash dump folder, store folder path in self.crash_dump
        and create parent directory if it doesn't exist already.
        """
        self.crash_dump = os.path.normpath(
            os.path.join(self.output_dir, "crash_dump", "crash_dump.json"))
        os.makedirs(os.path.dirname(self.crash_dump), exist_ok=True)

    def initialise_logging(self) -> None:
        """Initialise logging."""
        self.logger = get_logger(self.exp_name, self.output_dir)

        # initialise video recording process
        self.recording_process = None

    def setup_platform(self) -> None:
        """Parses the graph and instantiates device objects for all nodes.
        Device objects are accessible as, using 'rotavap' as an example:
        self['rotavap'] or self.graph.nodes['rotavap']['obj'].
        """
        # Wait until all device are ready.
        self.wait_until_ready()
        self.logger.debug("All devices ready!")

    def initialise_executioners(self) -> None:
        """Instantiate executioners and expose them as attributes of self."""
        self.pump = PumpExecutioner(
            self.graph, self.simulation, self.crash_dump)
        self.stirrer = StirrerExecutioner(
            graph=self.graph, simulation=self.simulation)
        self.vacuum = VacuumExecutioner(
            graph=self.graph, simulation=self.simulation)
        self.chiller = ChillerExecutioner(
            graph=self.graph, simulation=self.simulation)
        self.camera = CameraExecutioner()

    ###########
    # LOCKING #
    ###########

    def request_lock(self, nodes: List[str], pid: str) -> bool:
        """Find if locking given nodes with given pid is possible. Return True
        if it is otherwise False. DOES NOT LOCK NODES (acquire_lock does this)!

        Args:
            nodes (List[str]): Nodes to lock
            pid (str): Pid to lock nodes with.

        Returns:
            bool: True if nodes can be locked, otherwise False.
        """
        # Find out if all nodes are available for locking
        can_lock = True
        for node in self.graph.nodes():
            if node in nodes:
                if not self.graph[node]['lock'] in [None, pid]:
                    can_lock = False
        return can_lock

    def acquire_lock(self, nodes: List[str], pid: str):
        """Acquire lock on given nodes using given pid. request_lock should be
        called before this and return True, otherwise errors will be raised.

        Args:
            nodes (List[str]): Nodes to lock.
            pid (str): Identifier to lock nodes with.

        Returns:
            bool: True if locking was successful, otherwise False.
        """
        for node in self.graph.nodes():
            if node in nodes:
                # Raise error if attempt is made to lock node already locked by
                # a different pid.
                if self.graph[node]['lock'] not in [None, pid]:
                    raise IllegalLockError(
                        f'{node} is already locked by pid\
 {self.graph[node]["lock"]}')

                # If no IllegalLockError raised, go ahead and lock node
                self.graph[node]['lock'] = pid

    def release_lock(self, nodes: List[str], pid: str):
        """Release lock on given nodes with given locking pid.

        Args:
            nodes (List[str]): Nodes to unlock.
            pid (str): Pid that nodes being unlocked must be locked with.
        """
        for node in self.graph.nodes():
            if node in nodes and self.graph[node]['lock'] == pid:
                self.graph[node]['lock'] = None

    #################
    # MISCELLANEOUS #
    #################

    def wait(self, wait_time: int) -> None:
        """
        Wait for a desired time and prints the wait progress.

        Args:
            wait_time (int): Time to wait in seconds
        """
        if self.simulation:
            self.logger.info("Waiting for {0} seconds...".format(wait_time))

        else:
            # Initialise time variables.
            start_time = time.time()
            end_time = start_time + wait_time
            end_time = time.localtime(end_time)
            end_time_pretty_print = time.strftime("%Y-%m-%d %H:%M:%S", end_time)
            self.logger.info(
                "Waiting will be done at approximately {0}".format(
                    end_time_pretty_print))
            percent_done = 0

            # While waiting, continuously log % until wait is over.
            time_elapsed = round(time.time() - start_time)
            while time_elapsed < wait_time:
                new_percent_done = math.floor(
                    100 * (time.time() - start_time) / wait_time)
                # If % done is different, log time reamining.
                if (new_percent_done > percent_done):
                    percent_done = math.floor(
                        100 * (time.time() - start_time) / wait_time)
                    time_remaining_seconds = (
                        start_time + wait_time - time.time())
                    # Split time remaining into hours, minutes and seconds
                    hours = math.floor(time_remaining_seconds / 3600)
                    minutes = math.floor(
                        (time_remaining_seconds - (hours * 3600)) / 60)
                    seconds = round(
                        time_remaining_seconds
                        - (hours * 3600)
                        - (minutes * 60))
                    self.logger.debug(
                        "Waiting to {0}% done. Approximately {1} h, {2} min,\
 {3} sec remaining.".format(percent_done, hours, minutes, seconds))

                # Update time elapsed and continue.
                time.sleep(0.5)
                time_elapsed = round(time.time() - start_time)

            self.logger.info("Waiting done.")

    def wait_until_ready(self) -> None:
        """Call wait_until_ready on the device object for every node in the
        graph.
        """
        for node in self:
            if hasattr(self[node], "wait_until_ready"):
                self[node].wait_until_ready()

    def breakpoint(self) -> None:
        """
        Delay execution of the script until the user prompts it to resume or
        cancel operation.
        """
        # wait for all current operations to finish first
        self.wait_until_ready()

        while True:
            self.logger.debug("Breakpoint reached.")
            answer = input(
                "Breakpoint reached. Continue operation? (y/N) ").lower()
            if answer == "y" or answer == "Y":
                self.logger.info("Resuming operation...")
                break
            else:
                sys.exit(0)

    def start_recording(self, camera_id: Optional[int] = 1) -> None:
        """
        Start the recording of a log video.

        Args:
            camera_id (int): ID of camera to start recording.
        """
        self.logger.info("Starting log video recording...")
        # spawn queues
        message_queue = queue.Queue()
        recording_speed_queue = queue.Queue()

        # create logging message handlers
        video_handler = VlogHandler(message_queue)
        recording_speed_handler = VlogHandler(recording_speed_queue)

        # set logging levels
        video_handler.setLevel(logging.INFO)
        recording_speed_handler.setLevel(5)  # set a logging level below DEBUG

        # only allow dedicated messages for the recording speed handler
        speed_filter = RecordingSpeedFilter()
        recording_speed_handler.addFilter(speed_filter)

        # attach the handlers
        self.logger.addHandler(video_handler)
        self.logger.addHandler(recording_speed_handler)

        # work out video name and path
        video_dir = os.path.join(self.output_dir, "log_videos")
        # create video directory if it doesn't exist
        os.makedirs(video_dir, exist_ok=True)
        i = 0
        while True:
            video_path = os.path.join(video_dir, "{0}_{1}.avi".format(
                self.exp_name, i))
            # keep incrementing the file counter until you hit one that doesn't
            # yet exist
            if os.path.exists(video_path):
                i += 1
            else:
                break

        # launch recording process
        self.recording_process = threading.Thread(
            target=recording_worker,
            daemon=True,
            args=(message_queue, recording_speed_queue, video_path, camera_id))
        self.recording_process.start()
        time.sleep(5)  # wait for the video feed to stabilise

        self.logger.info('Done. Log video is located in "{0}".'.format(
            video_path))

    def rebuild_graph(self) -> None:
        """
        Rebuild the graph from the crash dump.
        """
        with open(self.crash_dump) as f_d:
            graph_data = json.load(f_d)

        for each_node in self.graph.nodes():
            saved_node = graph_data.get(each_node)
            if not saved_node:
                continue
            for key in self.graph[each_node].keys():
                saved_value = saved_node.get(key)
                if saved_value:
                    self.graph[each_node][key] = saved_value

    def disconnect(self) -> None:
        """
        Disconnect from all _ChemputerEthernetDevices and SerialDevices.
        Calling this function allows Chempiler to be reinstantiated within the
        same Python process.
        """
        for node in self.graph.nodes:
            node_obj = self.graph.obj(node)
            if hasattr(node_obj, "disconnect"):
                node_obj.disconnect()

    #################
    # MAGIC METHODS #
    #################

    def __iter__(self) -> Generator[str, None, None]:
        """Yields every node in graph."""
        for node in self.graph:
            yield node

    def __getitem__(self, node_name: str) -> Any:
        """
        Return instantiated device object associated with node_name given.

        Args:
            node_name (str): Name of node to get device object for.

        Returns:
            Any: Device object associated with node name.
        """
        return self.graph.obj(node_name)
