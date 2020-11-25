import logging

from SerialLabware import C3000
from .device import ChemputerDevice


class SimChemputerTricontC3000(ChemputerDevice):
    def __init__(self, port, address, clockwise=True, name="", num_positions=6, has_pump=True, **kwargs):
        self.port = port
        self.address = address
        self.clockwise = clockwise
        self.name = name
        self.num_positions = num_positions
        self.has_pump = has_pump

        self.logger = logging.getLogger("main_logger.sim_logger")

    @property
    def capabilities(self):
        num_positions = self.num_positions
        if self.has_pump:
            # sink from port 0...(num_positions-1)
            sink_ops = [("sink", i) for i in range(num_positions)]
            # source to port 0...(num_positions-1)
            source_ops = [("source", i) for i in range(num_positions)]
            return sink_ops + source_ops
        else:
            # route from port 0...(num_positions-1) to port -1 (syringe port)
            route_in_ops = [('route', i, -1) for i in range(num_positions)]
            # route from port -1 to port 0...(num_positions-1)
            route_out_ops = [('route', -1, i) for i in range(num_positions)]
            return route_in_ops + route_out_ops

    def execute(self, cmd, **kwargs):
        super().execute(cmd, **kwargs)


class ChemputerTricontC3000(SimChemputerTricontC3000):

    # class variable holding the shared connections to the various
    # serial ports
    CONNECTIONS = {}

    def __init__(self, port, address, clockwise=True, name="", num_positions=6, has_pump=True, **kwargs):
        super().__init__(port, address, name, num_positions, has_pump, **kwargs)
        self.logger = logging.getLogger("main_logger.serial_device_logger")

        if port not in self.CONNECTIONS:
            self.logger.debug(f"Openning new serial connection on port {port}.")
            self.device = C3000(port, name)
            self.device.open_connection()
            self.device.launch_command_handler()
            self.CONNECTIONS[port] = self.device
        else:
            self.logger.debug(f"Reusing serial connection on port {port}.")
            self.device = self.CONNECTIONS[port]
        self.device.init_pump_full(run=True, address=address)

    def execute(self, cmd, **kwargs):
        super().execute(cmd, **kwargs)
        # TODO: Add actuation code.
