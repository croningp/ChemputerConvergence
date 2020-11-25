import socket
from .device import ChemputerDevice
from .pump_valve_api import _SimChemputerEthernetDevice

BUF = 1024

#TODO This should be provided in the graph
TCP_PORT = 5000

class PneumaticController(ChemputerDevice):
    def __init__(self, device_name: str, address: str) -> None:
        self.name = device_name
        self.client = self.connect_to_board(address)
        # These should match names of commands defined
        # for the CommandManager on the Arduino side
        self.channel_commands = {
            1: ("a3", "a2"),
            2: ("a5", "a4"),
            3: ("a7", "a6"),
            4: ("a9", "a8"),
            5: ("a11", "a10"),
            6: ("a13", "a12")
        }

    def connect_to_board(self, address: str) -> socket.socket:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Timeout has to be set after socket creation
        # Otherwise socket connect()/recv() might block forever
        client.settimeout(0.1)
        try:
            # Here should be a tuple of IP address and port
            client.connect((address, TCP_PORT))
        except Exception:
            raise ConnectionError(
                f'Unable to connect to Arduino: {address}:{TCP_PORT}')
        return client

    def build_cmd(
        self, pin_name: str, mode: str, value: int = None) -> str:
        if mode == 'R':
            return f'{pin_name},R;'
        if mode == 'W' and value is not None:
            return f'{pin_name},W,{value};'
        return None

    def read_pin(self, pin_name: str) -> bytes:
        self.send(self.build_cmd(pin_name, 'R'))
        return self.receive()

    def write_pin(self, pin_name: str, value: int) -> bytes:
        self.send(self.build_cmd(pin_name, 'W', value))
        return self.receive()

    def send(self, cmd: str) -> None:
        self.client.sendall(cmd.encode('utf-8'))

    def receive(self) -> bytes:
        # Minimal error handling is necessary here
        # In case of success Commanduino doesn't return any message
        # So timeout exception should be handled properly
        try:
            chunk = self.client.recv(BUF)
            return chunk.decode("utf-8")
        except socket.timeout:
            pass
        except UnicodeDecodeError:
            raise ConnectionError("Can't decode device reply <{}> !".format(chunk)) from None

    def switch_vacuum(self, channel):
        self.write_pin(self.channel_commands[channel][0], 255)
        self.write_pin(self.channel_commands[channel][1], 0)

    def switch_argon(self, channel, pressure='low'):
        if pressure == 'low':
            self.write_pin(self.channel_commands[channel][0], 0)
            self.write_pin(self.channel_commands[channel][1], 0)

        elif pressure == 'high':
            self.write_pin(self.channel_commands[channel][0], 0)
            self.write_pin(self.channel_commands[channel][1], 255)


    def __del__(self) -> None:
        self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()

class ConnectionError(Exception):
    pass

class SimPneumaticController(_SimChemputerEthernetDevice):
    def switch_argon(self, channel, pressure='low'):
        self.logger.info(
            f'Switching channel {channel} to argon ({pressure} pressure).')

    def switch_vacuum(self, channel):
        self.logger.info(f'Switching channel {channel} to vacuum.')
