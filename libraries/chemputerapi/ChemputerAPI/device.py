import logging

class ChemputerDevice:
    """Fallback functionality for Chemputer devices."""
    def __init__(self, name, **kwargs):
        self.name = name
        self.logger = logging.getLogger("main_logger.device_logger")

    def execute(self, cmd, **cmd_params):
        device_type = type(self).__name__
        if hasattr(self, 'capabilities') and cmd not in self.capabilities:
            raise ValueError(f"{device_type} {self.name} - Command {cmd}, parameters = {cmd_params}).")
        self.logger.debug(f"{device_type} {self.name} - Received command {cmd}, parameters = {cmd_params}).")

    def wait_until_ready(self):
        pass

class ChemputerDeviceError(Exception):
    pass
