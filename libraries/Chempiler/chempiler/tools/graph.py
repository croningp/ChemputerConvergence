import json
import copy
import networkx as nx
from . import constants
from .errors import ChempilerError
import inspect
import logging
from itertools import chain
from networkx.exception import NetworkXNoPath
from networkx.readwrite.json_graph import node_link_graph
from networkx.algorithms.shortest_paths import shortest_path_length
from typing import (
    Dict, Any, Optional, Union, List, Iterable, Tuple, Generator
)
from types import ModuleType
from ChemputerAPI import ChemputerDevice, ChemputerPump

##########################
# Loading networkx graph #
##########################

def load_graph(
    graph_file: Union[str, Dict[str, List[Dict[str, Any]]]],
    graph_type: Optional[str] = None
) -> nx.MultiDiGraph:
    """
    Load graph containing Chemputer devices. Discards unnecessary
    information and relabels the nodes.

    Args:
        graph_file (Union[str, Dict[str, List[Dict[str, Any]]]]): Three options:
            1) Path to GraphML file.
            2) Path to JSON node link graph file.
            3) JSON node link graph as dict.
        graph_type (str): None, "json" or "graphml". If None, graph_type will be
            determined from the file extension.

    Returns:
        nx.MultiDiGraph: Sanitised graph object.
    """
    # Create MultiDiGraph object.
    if graph_file:

        # If dict of JSON node link graph supplied create MultiDiGraph using
        # networkx method node_link_graph.
        if isinstance(graph_file, dict):
            graph = node_link_graph(graph_file, directed=True, multigraph=True)

        # If file path is supplied.
        elif isinstance(graph_file, str):

            # If graph_type is not supplied work it out from the file path.
            if not graph_type:
                graph_type = graph_file.split(".")[-1].lower()

            # Load JSON to dict, and create graph from dict.
            if graph_type == "json":
                with open(graph_file, "r") as fileobj:
                    json_graph_dict = json.load(fileobj)

                    # Check no duplicate names
                    used_names = []
                    for node in json_graph_dict['nodes']:
                        name = node['name']
                        if name in used_names:
                            raise ChempilerError(f'Cannot use same name for two\
 different node: "{name}"')
                        used_names.append(name)

                    graph = node_link_graph(
                        json_graph_dict, directed=True, multigraph=True)

            # Directly load graphML.
            elif graph_type == "graphml":
                graph = nx.MultiDiGraph(nx.read_graphml(graph_file))

        # Invalid file path supplied.
        else:
            raise ValueError(
                'Invalid graph file supplied. Accepted file extensions are\
 ".graphml" and ".json".')

    # No graph supplied.
    else:
        raise ValueError("Invalid graph supplied.")

    return graph


def port_parse(port_name: str) -> Union[int, str]:
    """
    Tries to parse `port_name` as an integer. Return `port_name` unchanged
    if that fails.
    """
    try:
        return int(port_name)
    except ValueError:
        return port_name


def edge_parse(edge_text: str) -> Tuple[Union[int, str]]:
    """
    parses input/output ports described by a graph edge: (src_port, dst_port)
    """
    # remove surrounding space and parens
    t = edge_text.strip()[1:-1]
    src_port, dst_port = t.split(",")

    return (port_parse(src_port.strip()), port_parse(dst_port.strip()))


def sanitise_graph(graph: Dict) -> nx.MultiDiGraph:
    """Sanitises the graph by removing unnecessary params and renaming others

    Arguments:
        graph {Dict} -- Graph to clean

    Returns:
        nx.MultiDiGraph -- Sanitised graph
    """

    # Rename label attribute to name.
    mapping = {}
    for node in graph.nodes():
        label = str(graph.nodes[node].pop("label", "NaN"))
        graph.nodes[node]["name"] = label
        mapping[node] = label
    graph = nx.relabel_nodes(graph, mapping)

    for node in graph.nodes():
        # Remove irrelevant attributes x and y.
        graph.nodes[node].pop("x", None)
        graph.nodes[node].pop("y", None)

        # Add default None lock status
        graph.nodes[node]['lock'] = None

    # Process edge attrs, parses '(0, 1)' port strings to determine edge source
    # and destination ports.
    for edge in graph.edges:
        if "port" in graph.edges[edge]:
            graph.edges[edge]["port"] = edge_parse(graph.edges[edge]["port"])

    return graph


def devices(modules: Iterable[ModuleType], simulation: bool) -> Dict[str, type]:
    """
    Given a set of modules, each containing device classes, return a
    dictionary of { device_class_name: DeviceClass }.

    Args:
        modules (Iterable[ModuleType]): The modules to probe for devices.
            e.g. [ChemputerAPI, SerialLabware]. Any class within the top level
            of each module is used.
        simulation (bool): If true, the return dict is of the form:
            { DeviceClassName: SimulationDeviceClass }. If no simulation device
            is available for a certain device, the original class is used. This
            is fine for stuff like ChemputerFlask as the flask doesn't do
            anything so no SimChemputerFlask class is needed.

    Returns:
        device_dict (Dict[str, type]): Dict of device class names and their
            respective classes, i.e. { device_class_name: DeviceClass }.
    """
    # Get all classes within the top level of each modules.
    result = []
    for module in modules:
        result.extend(inspect.getmembers(module, inspect.isclass))
    device_dict = dict(result)

    # Rename all 'SimDevice' classes to 'Device'. This means that all
    # { device_name: DeviceClass } pairs in the dict become
    # { device_name: SimDeviceClass }. No matter what the simulation flag is
    # DeviceClasses are accessed using the device_name so the SimDeviceClasses
    # have to be attached to the device_names here.
    if simulation:
        sim_devices = {
            dev_name[3:]: device_dict[dev_name]  # Remove 'Sim' from device_name
            for dev_name in device_dict
            if dev_name.startswith("Sim")
        }
        device_dict.update(sim_devices)

    return device_dict


##################
# ChempilerGraph #
##################

class ChempilerPathStep(object):
    """Convenience class for steps in a path through the graph.

    Args:
        src (str): Name of source node in step.
        dest (str): Name of destination node in step.
        src_port (Optional[Union[int, str]]): Source port in step.
        dest_port (Optional[Union[int, str]]): Destination port in step.
    """
    def __init__(
        self,
        src: str,
        dest: str,
        src_port: Optional[Union[int, str]] = None,
        dest_port: Optional[Union[int, str]] = None
    ) -> None:

        self.src = src
        self.dest = dest
        self.src_port = src_port
        self.dest_port = dest_port

    def as_tuple(self):
        return (self.src, self.dest, (self.src_port, self.dest_port))

    def __repr__(self):
        return f"({self.src}, {self.dest}, ({self.src_port}, {self.dest_port}))"


# Long ago when man was King, his heart did speak of a Stained Class...
class ChempilerGraph:
    """Class to represent the Chemputer topology.
    Wrapper around the NetworkX definition with Chemputer additions

    Args:
        filename (str): Name of the graph file
            - Currently supports GraphML and JSON
        logger (logging.Logger): Logging module
    """

    ##################
    # Initialisation #
    ##################

    def __init__(
        self,
        filename: str,
        logger: logging.Logger,
        device_modules: List[ModuleType],
        simulation: bool = False
    ):
        # Load up the graph file into NetworkX
        self.graph = load_graph(filename)
        self.raw_graph = copy.deepcopy(self.graph)
        self.graph = sanitise_graph(self.graph)

        # Logging
        self.logger = logger

        # Simulation
        self.simulation = simulation

        # Explicitly populate of flag set
        if device_modules:
            self.populate(device_modules)

        # Find the backbone topology
        self.backbone = self.find_backbone()

        # Nodes wrapper
        self.nodes = self.graph.nodes

        # Edge wrapper
        self.edges = self.graph.edges

    def node_can_route(self, node, ports=()):
        obj = self.graph.nodes[node]["obj"]
        if hasattr(obj, "capabilities"):
            capabilities = obj.capabilities
            if ports:
                return ("route", ports[0], ports[1]) in capabilities

            return any([item[0] == "route" for item in capabilities])
        return False

    def node_can_pump(self, node):
        obj = self.graph.nodes[node]["obj"]
        if hasattr(obj, "capabilities"):
            return "pump" in obj.capabilities
        return False

    def node_is_valve(self, node):
        return self[node]["class"] == "ChemputerValve"

    def find_backbone(self) -> List[str]:
        """Finds the backbone of the Chemputer

        Chemputer backbone is defined as all valves with at least one other
        valve and a pump attached.

        Returns:
            List[str]: List of nodes that comprise the backbone.
        """

        # Get all valve nodes
        valve_nodes = [
            n for n in self.graph.nodes
            if self.node_can_route(n)
        ]

        # Define the backbone
        backbone = []

        # Iterate through every nbode
        for node in valve_nodes:
            # Set flags for if the node has a valve neighbour and pump neighbour
            node_has_valve_neighbor = False
            node_has_pump_neighbor = False

            # Iterate through all neighbours of the current node
            for neighbor in nx.neighbors(self.graph, node):
                # If the neighbour is a valve, set the valve flag
                if self.node_can_route(neighbor):
                    node_has_valve_neighbor = True

                # If the neighbour is a pump, set the pump flag
                if self.node_can_pump(neighbor):
                    node_has_pump_neighbor = True

            # If both flags are set, valve is in the backbone
            if node_has_pump_neighbor and node_has_valve_neighbor:
                backbone.append(node)

        # Return unique list of valves in the backbone
        return list(set(backbone))

    def instantiate_node(self, node: str, devs: Dict[str, type]) -> None:
        attrs = self.graph.nodes[node]
        node_class = devs[attrs["class"]]
        params = inspect.getfullargspec(node_class)
        self.logger.debug(
            f"Instantiating node {node}:\n\tclass = {node_class.__name__},\
\n\tparams = {params.args},\n\tgraph attrs = {attrs}.")

        # SerialLabware uses device_name not name in constructors.
        if 'name' in attrs:
            attrs['device_name'] = attrs['name']

        # Device constructor takes **kwargs, pass everything.
        if params.varkw:
            attrs["obj"] = node_class(**attrs)

        # Device constructor takes specific params, only pass those
        else:
            attrs = {
                param: attrs[param]
                for param in attrs
                if param in params.args
            }
            self.graph.nodes[node]["obj"] = node_class(**attrs)
        self.logger.debug(f"Node {node} instantiated.")

    def populate(self, modules: List) -> None:
        """Populates the graph with ChemputerDevice objects and paramters

        Args:
            modules (List): List of Chemputer modules e.g. ChemputerAPI,
                SerialLabware etc.
            simulation (bool): Simulation run
        """

        # Get all DeviceObjects
        devs = devices(modules, self.simulation)

        pumps = [node for node in self.graph
                 if self.graph.nodes[node]['class'] == 'ChemputerPump']
        valves = [node for node in self.graph
                  if self.graph.nodes[node]['class'] == 'ChemputerValve']
        other_nodes = [
            node for node in self.graph
            if self.graph.nodes[node]['class'] not in [
                'ChemputerPump', 'ChemputerValve']
        ]
        # Instantiate non pump/valve nodes.
        for node in other_nodes:
            self.instantiate_node(node, devs)

        # Instantiate valves first so that they switch to an appropriate
        # position.
        # before pumps instantiate and push down any liquid they may still
        # contain.
        for node in valves:
            self.instantiate_node(node, devs)
        for node in valves:
            self.obj(node).wait_until_ready()

        # Instantiate pumps after valves.
        for node in pumps:
            self.instantiate_node(node, devs)
        for node in pumps:
            self.obj(node).wait_until_ready()

    ########################
    # Full path generation #
    ########################

    def subpath_generator(self, path: List[str]) -> List[List[str]]:
        """Yields a subpath from a supplied path
        E.g ['flask1', 'valve1', 'valve2', 'valve3', 'flask2]
        This path would yield ['flask1', 'valve1'] until all combinations of
        the path are complete.

        Arguments:
            path (List[str]): Path to generate subpaths from

        Returns:
            List[List[str]]: Subpath
        """

        for pos, _ in enumerate(path):
            if pos + 1 == len(path):
                break
            yield [path[pos], path[pos + 1]]

    def get_full_paths(self, path: List[str]) -> List[List[ChempilerPathStep]]:
        """Given simple path as list of node names, return full paths as list of
        tuples with ports e.g. ['flask_water', 'valve1', 'filter'] -->
        [['flask_water', 'valve1', (0, 2)], ['valve1', 'filter', (3, 'top')]]

        Args:
            path (List[str]): Simple path of just node names e.g.
                ['flask_water', 'valve1', 'filter']

        Returns:
            List[List[ChempilerStep]]: Full path of all steps in simple path
                with ports included. List of paths returned as one simple path
                can give rise to multiple full paths if certain steps can use
                different ports on a node.
        """

        # Get all possible edges for every subpath in path.
        subpaths = [sp for sp in self.subpath_generator(path)]
        path_edges = []
        for subpath in subpaths:
            subpath_edges = []
            for src, dest, edge_data in self.edges.data():
                if src == subpath[0] and dest == subpath[1]:
                    subpath_edges.append([src, dest, edge_data["port"]])
            path_edges.append(subpath_edges)

        # Build all paths from all combinations of edges associated with
        # subpaths.
        full_paths = []
        go_again = True
        while go_again:
            go_again = False
            path = []
            for step_edges in path_edges:
                if len(step_edges) == 1:
                    src, dest, ports = step_edges[0]
                    path.append(ChempilerPathStep(
                        src, dest, ports[0], ports[1]))

                elif len(step_edges) > 1:
                    src, dest, ports = step_edges.pop()
                    path.append(ChempilerPathStep(
                        src, dest, ports[0], ports[1]))

                    # If multiple options at this subpath there are still more
                    # paths to build so keep going.
                    go_again = True

            full_paths.append(path)
        return full_paths

    ##########################
    # Invalid path filtering #
    ##########################

    def filter_invalid_paths(
        self,
        paths: List[List[ChempilerPathStep]],
        src_port: Optional[Union[int, str]] = None,
        dest_port: Optional[Union[int, str]] = None,
        connect: Optional[bool] = False,
        partial_path: Optional[bool] = False,
    ) -> List[List[ChempilerPathStep]]:
        """Filter out paths that are invalid.

        Args:
            paths (List[ChempilerPathStep]): List of paths to filter.
            src_port (Optional[Union[int, str]]): Source port of desired path.
            dest_port (Optional[Union[int, str]]): Dest port of desired path.
            connect (Optional[bool]): True if just connecting valves, not
                moving liquid.

        Returns:
            List[List[ChempilerPathStep]]: Path list with invalid paths removed.
        """
        # Full liquid movement paths must contain a valve connected to a pump.
        if not partial_path and not connect:
            paths = self.filter_movement_paths_with_no_pumps(paths)

        # Filter out paths where the src and dest port aren't correct
        paths = self.filter_invalid_src_dest_paths(paths, src_port, dest_port)

        # Filter out paths where routing valves are routing without using -1
        paths = self.filter_invalid_routing_valve_paths(paths, connect=connect)
        return paths

    def filter_invalid_routing_valve_paths(
        self,
        paths: List[List[ChempilerPathStep]],
        connect: Optional[bool] = False,
    ) -> List[List[ChempilerPathStep]]:

        """Remove any paths from path list where a routing valve has to route
        between two ports where neither port is -1. This is impossible as valves
        can only route through the central (-1) port.

        Args:
            paths (List[List[ChempilerPathStep]]): List of paths to filter.
            connect (Optional[bool]): True if no liquid movement, just valve
                connection.

        Returns:
            List[List[ChempilerPathStep]]: paths with any paths containing
                impossible routing operations removed.
        """

        # Check all valve routing operations use the -1 port as you can't
        # route without using the central port.
        for i in reversed(range(len(paths))):
            path = paths[i]
            for j in range(1, len(path)):
                step = path[j]
                prev_step = path[j - 1]

                # If valve node is routing valve (connect or not attached to
                # pump)
                if (self.node_can_route(step.src)
                    and (connect
                         or not self.get_pump_from_valve_name(step.src))):

                    # Check routing ports are valid
                    if not self.node_can_route(
                            step.src, (prev_step.dest_port, step.src_port)):
                        paths.pop(i)
                        break
        return paths

    def filter_invalid_src_dest_paths(
        self,
        paths: List[List[ChempilerPathStep]],
        src_port: Union[int, str],
        dest_port: Union[int, str]
    ) -> List[List[ChempilerPathStep]]:

        """Filter out paths where the source port and dest port of the path
        don't match the desired source port and dest port.

        Args:
            paths (List[List[ChempilerGraph]]): Paths to filter.
            src_port (Union[int, str]): Desired source port.
            dest_port (Union[int, str]): Desired dest port.

        Returns:
            List[List[ChempilerPathStep]]: Paths with ones with the incorrect
                source port or dest port removed.
        """

        # Loop through each path and check for removal
        for i in reversed(range(len(paths))):
            path = paths[i]

            dest_valid = True
            # Destination port is incorrect
            if dest_port and path[-1].dest_port != dest_port:
                dest_valid = False

            src_valid = True
            # Source port is incorrect
            if src_port and path[0].src_port != src_port:
                src_valid = False

            if not src_valid or not dest_valid:
                paths.pop(i)

        return paths

    def filter_movement_paths_with_no_pumps(
        self,
        paths: List[List[ChempilerPathStep]],
        connect: Optional[bool] = False,
    ) -> List[List[ChempilerPathStep]]:

        """Remove any paths from path list where a routing valve has to route
        between two ports where neither port is -1. This is impossible as valves
        can only route through the central (-1) port.

        Args:
            paths (List[List[ChempilerPathStep]]): List of paths to filter.
            connect (Optional[bool]): True if no liquid movement, just valve
                connection.

        Returns:
            List[List[ChempilerPathStep]]: paths with any paths containing
                impossible routing operations removed.
        """
        if connect:
            return paths

        for i in reversed(range(len(paths))):
            path = paths[i]
            if not any([self.get_pump_from_valve_name(step.src)
                        for step in path[1:]]):
                paths.pop(i)

        return paths

    ###############
    # Pathfinding #
    ###############

    def find_alternative_path(
        self,
        src: str,
        dest: str,
        src_port: Optional[Union[int, str]] = "",
        dest_port: Optional[Union[int, str]] = "",
        recursion_level: int = 0,
    ):
        """Attempts to find an alternate path when a usual path cannot be found
        This is for the situation in which liquid must be routed through a
        valve, to a valve with a pump, then back through the first valve to a
        different flask.
        Flask A -> Valve B -> Valve C -> Pump C -> Valve C -> Valve B -> Flask B
        This splits the path into two, Flask A -> Pump C and Pump C -> Flask B
        and returns both paths separately.

        Args:
            src (str): Src node
            dest (str): Destination node
            src_port (str): Port on src node.
            dest_port (str): Port on dest node.
            recursion_level (int): Recursion level passed from find_optimal_path
                Passed back to find_optimal_path to ensure alternative paths
                are not looked for within alternative paths.

        Returns:
            List[List[Tuple[str]]]: [forward_path, backward_path]
        """
        # Find closest pump to node
        shortest_pump_path_length = 100000
        nearest_pump = None
        for node in self.graph:
            if self.node_can_pump(node):
                try:
                    pump_path_length = shortest_path_length(
                        self.graph, source=src, target=node)
                    if pump_path_length < shortest_pump_path_length:
                        shortest_pump_path_length = pump_path_length
                        nearest_pump = node
                except NetworkXNoPath:
                    pass

        if not nearest_pump:
            raise NetworkXNoPath(
                f"Cannot find normal or alternative path between {src} and\
 {dest}")

        # Find paths from src to pump, and pump to dest.
        src_to_pump = self.find_optimal_path(
            src,
            nearest_pump,
            src_port=src_port,
            recursion_level=recursion_level + 1
        )
        pump_to_dest = self.find_optimal_path(
            nearest_pump,
            dest,
            dest_port=dest_port,
            recursion_level=recursion_level + 1
        )

        # Check paths found are valid
        src_to_pump = self.filter_invalid_paths(
            [src_to_pump], src_port=src_port)[0]
        pump_to_dest = self.filter_invalid_paths(
            [pump_to_dest], dest_port=dest_port)[0]

        if not src_to_pump or not pump_to_dest:
            raise NetworkXNoPath(
                f"Cannot find normal or alternative path between {src} and\
 {dest}")

        return [src_to_pump, pump_to_dest]

    def find_optimal_path(
        self,
        src: str,
        dest: str,
        src_port: Optional[Union[int, str]] = "",
        dest_port: Optional[Union[int, str]] = "",
        use_backbone: Optional[bool] = True,
        connect: Optional[bool] = False,
        partial_path: Optional[bool] = False,
        recursion_level: int = 0,
    ) -> List[ChempilerPathStep]:

        """Finds the most optimal and shortest path through the graph form src
        to dest. If use_backbone is True, paths through the backbone will be
        favourted. Otherwise just the shortest path is returned.

        Args:
            src (str): Source node
            dest (str): Destination node
            src_port (Optional[Union[int, str]]): Port on the source node to
                use.
            dest_port (Optional[Union[int, str]]): Port on the destination node
                to use.
            use_backbone (Optional[bool]): Use the Chemputer backbone if
                possible. Defaults to True.
            connect (Optional[bool]): True if just valves being connected, no
                liquid movement, otherwise False.
            partial_path (Optional[bool]): Bool specifying whether path being
                found is part of a larger path (True), or is an entire path
                itself (False). Invalid paths are filtered differently depending
                on this.
            recursion_level (int): Level of recursion. Needed to stop
                alternative paths being found within alternative paths.

        Raises:
            NetworkXNoPath: No valid path found between the src and dest.

        Returns:
            List[ChempilerPathStep]: Most optimal path.
        """

        # Try and find all shortest paths from one node to another
        try:
            paths = [p for p in nx.all_simple_paths(self.graph, src, dest)]
        except NetworkXNoPath:
            raise NetworkXNoPath

        full_paths = []
        for path in paths:
            full_paths.extend(self.get_full_paths(path))

        valid_paths = self.filter_invalid_paths(
            full_paths,
            src_port,
            dest_port,
            connect=connect,
            partial_path=partial_path
        )
        # No Paths -- try and find alternate path
        if not valid_paths:
            if not connect and recursion_level == 0:
                self.logger.debug(
                    f"Unable to find path between {src} and {dest}\
 ({src_port},{dest_port}) -- Attempting alternate path..."
                )

                # Find alternate path
                alt_path = self.find_alternative_path(
                    src, dest,
                    src_port=src_port,
                    dest_port=dest_port,
                    recursion_level=recursion_level
                )

                # No alternate path, kill it
                if not alt_path:
                    raise NetworkXNoPath(
                        f"Cannot find normal or alternate path between {src}\
 ({src_port}) -- {dest} ({dest_port})"
                    )
                valid_paths = [alt_path]
            else:
                raise NetworkXNoPath(
                    f"Cannot find path between {src} ({src_port}) -- {dest}\
 ({dest_port})"
                )

        # Explicitly want to utilise backbone
        elif use_backbone:
            # Get all paths that pass through backbone
            in_backbone_paths = [
                p for p in valid_paths
                if p[0].dest in self.backbone and p[-1].src in self.backbone
            ]

            # No backbone paths, just return shortest path
            if not in_backbone_paths:
                src_in_backbone_paths = [
                    p for p in valid_paths if p[0].dest in self.backbone
                ]
                if not src_in_backbone_paths:
                    dest_in_backbone_paths = [
                        p for p in valid_paths if p[-1].src in self.backbone
                    ]
                    if not dest_in_backbone_paths:
                        return min(valid_paths, key=lambda x: len(x))
                    return min(dest_in_backbone_paths, key=lambda x: len(x))
                return min(src_in_backbone_paths, key=lambda x: len(x))

            # Return the shortest path if there are backbone paths
            return min(in_backbone_paths, key=lambda x: len(x))

        # Only one path, follow it
        if len(valid_paths) == 1:
            return valid_paths[0]

        # Get the shortest path length
        shortest_path_length = min([
            len(elem) for elem in valid_paths
        ])

        # Get the list of shortest paths
        shortest_paths = [
            p for p in valid_paths
            if len(p) == shortest_path_length
        ]

        # Only one, return it
        if len(shortest_paths) == 1:
            return shortest_paths[0]

        # More than one path, default to the backbone
        elif len(shortest_paths) > 1:
            return self.find_optimal_path(
                src, dest, src_port, dest_port, use_backbone=True,
                connect=connect,
            )

        # Just in case
        return min(valid_paths, key=lambda x: len(x))

    def assign_default_port(self, src_or_dest, node, port):
        """Assign default port if port not explicitly given."""
        if port not in ['', None]:
            return port

        node_class = self[node]['class']
        DEFAULT_PORTS = constants.DEFAULT_PORTS

        if node_class in DEFAULT_PORTS:
            if src_or_dest == 'src':
                port = DEFAULT_PORTS[node_class]['src']

            elif src_or_dest == 'dest':
                port = DEFAULT_PORTS[node_class]['dest']

            else:
                raise ValueError(
                    f'src_or_dest argument must be one of "src" or "dest".\
 "{src_or_dest}" is invalid.')

        return port

    def find_path(
        self,
        src: str,
        dest: str,
        src_port: Optional[str] = "",
        dest_port: Optional[str] = "",
        through: Optional[Union[str, List[str]]] = "",
        use_backbone: Optional[bool] = True,
        connect: Optional[bool] = False,
    ) -> List[ChempilerPathStep]:

        """Finds the most optimal/shortest path from src to dest
        Gives the optional choice for going through specific nodes.

        Args:
            src (str): Source node
            dest (str): Destination node
            src_port (Optional[Union[int, str]]): Port on the source node to
                use.
            dest_port (Optional[Union[int, str]]): Port on the destination node
                to use.
            through (Optional[Union[List[str], str]]): Node(s) to go through in
                path from src to dest.
            use_backbone (Optional[bool]): Use the Chemputer backbone if
                possible. Defaults to True.
            connect (Optional[bool]): True if just valves being connected, no
                liquid movement, otherwise False.

        Raises:
            TypeError: Through nodes are not string or list

        Returns:
            List[ChempilerPathStep]: List of steps in path.
        """
        if not through:
            # No through nodes, just return path from src, to dest
            return self.find_optimal_path(
                src, dest, src_port, dest_port, use_backbone=use_backbone,
                connect=connect, partial_path=False
            )

        # Through single node
        if (isinstance(through, str)
                or (isinstance(through, list) and len(through) == 1)):
            if type(through) == list:
                through = through[0]
            # Get path from src to through node
            first_path = self.find_optimal_path(
                src,
                through,
                src_port=src_port,
                dest_port=self.assign_default_port('dest', through, None),
                use_backbone=False,
                connect=connect,
                partial_path=True,
            )

            self.logger.debug(
                f'Found path from  {src} to {through}: {first_path}')

            # Through path should not visit dest node before end of path.
            if dest in [step.src for step in first_path]:
                raise NetworkXNoPath(
                    f'Cannot find path from {src} to {dest} through {through}\
 without going through {dest} during path.')

            # Get path from through node to dest
            second_path = self.find_optimal_path(
                through,
                dest,
                src_port=self.assign_default_port('src', through, None),
                dest_port=dest_port,
                use_backbone=False,
                connect=connect,
                partial_path=True,
            )
            self.logger.debug(
                f'Found path from {through} to {dest}: {second_path}')

            # Join paths together
            if first_path[-1].src == second_path[0].dest:
                full_path = [first_path, second_path]
                self.logger.debug(f'Full path: {full_path}')
                return full_path
            else:
                full_path = list(chain(first_path, second_path))

                if self.filter_invalid_paths(
                    [full_path],
                    src_port=src_port,
                    dest_port=dest_port,
                    connect=connect,
                    partial_path=False
                ):
                    self.logger.debug(f'Full path: {full_path}')
                    return full_path
                else:
                    raise NetworkXNoPath(
                        f'Cannot find valid path from {src} to {dest} through\
 {through}.')

        # Through multiple nodes
        if isinstance(through, list):

            # Get the intital path from src to first through node
            initial_path = self.find_optimal_path(
                src,
                through[0],
                src_port,
                dest_port=self.assign_default_port('dest', through[0], None),
                use_backbone=False,
                connect=connect,
                partial_path=True,
            )
            through_src = through[0]

            # Get all paths between the through nodes
            middle_paths = []
            for item in through[1:]:
                middle_paths.append(
                    self.find_optimal_path(
                        through_src,
                        item,
                        src_port=self.assign_default_port(
                            'src', through_src, None),
                        dest_port=self.assign_default_port('dest', item, None),
                        use_backbone=False,
                        connect=connect,
                        partial_path=True,
                    )
                )
                through_src = item

            # Get the last path from the last through node to dest
            final_path = self.find_optimal_path(
                through[-1],
                dest,
                src_port=self.assign_default_port('src', through[-1], None),
                dest_port=dest_port,
                use_backbone=False,
                connect=connect,
                partial_path=True,
            )

            # Join paths together
            full_path = initial_path
            alt_path = False
            for path in middle_paths:
                # valve_separator -> flask_separator -> valve_separator
                # Need to treat as alt path going to separator then coming from
                # separator
                # See tests/test_pipelining DMP_graph_test tests
                if full_path[-1].src == path[0].dest:
                    if not alt_path:
                        alt_path = True
                        full_path = [full_path]
                    full_path.append(path)
                else:
                    if alt_path:
                        full_path[-1].extend(path)
                    else:
                        full_path += path

            if not alt_path:
                full_path += final_path
            else:
                full_path[-1].extend(final_path)

            if type(full_path[0]) != list:
                if self.filter_invalid_paths(
                    [full_path],
                    src_port=src_port,
                    dest_port=dest_port,
                    connect=connect,
                    partial_path=False,
                ):
                    return full_path
                else:
                    raise NetworkXNoPath(
                        f'Cannot find valid path from {src} to {dest} through\
 {through}.')

            else:
                return full_path

        # You failed at following basic instructions....
        raise TypeError("Through parameter must be a list, string, or empty!")

    #################
    # Miscellaneous #
    #################

    def get_pump_from_valve_name(self, valve_name: str) -> ChemputerPump:
        """Gets the attached pump name and object from a ChemputerValve

        Arguments:
            valve_name (str): Name of the valve

        Returns:
            ChemputerPump: ChemputerPump object
        """

        pump = [
            x for x in self.graph.neighbors(valve_name)
            if self.node_can_pump(x)
        ]

        if pump:
            return self.obj(pump[0])
        return None

    def obj(self, key: str) -> ChemputerDevice:
        """Gets the object associated with the given name

        Arguments:
            key (str): Name of the node

        Raises:
            KeyError: If key is not in the graph.

        Returns:
            obj: ChemputerDevice object
        """

        try:
            return self.graph.nodes[key]["obj"]
        except KeyError:
            raise KeyError(f"No node by the name of {key}")

    def predecessors(self, node_name: str) -> Generator[str, None, None]:
        """Wrapper around networkx predecessors() method
        So not to break compatibility with other modules

        Args:
            node_name (str): Name of the node

        Yield:
            str: Predecessor node name
        """

        for item in self.graph.predecessors(node_name):
            yield item

    def neighbors(self, node_name: str) -> Generator[str, None, None]:
        """Gets all neighboring nodes from a given node

        Args:
            node_name (str): Name of the node

        Yields:
            str: Neighboring node name
        """

        for item in self.graph.neighbors(node_name):
            yield item

    def __getitem__(self, key: str) -> Dict:
        """Returns the node of the graph matching the key

        Arguments:
            key (str): Node to retrieve

        Returns:
            Dict[str, Any]: Node information
        """

        return self.graph.nodes[key]

    def __iter__(self):
        for node in self.graph.nodes():
            yield node
