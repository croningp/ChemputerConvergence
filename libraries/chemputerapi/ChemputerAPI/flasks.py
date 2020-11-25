import logging

from .device import ChemputerDevice


class ChemputerFlask(ChemputerDevice):
    def __init__(self, name, current_volume=0.0, max_volume=0.0, **kwargs):
        self.name = name
        self.current_volume = float(current_volume)
        self.max_volume = float(max_volume)

        self.logger = logging.getLogger("main_logger.flask_logger")

    @property
    def capabilities(self):
        return [("source", 0), ('sink', 0)]

    def execute(self, cmd, volume, **kwarg):
        if cmd[0] == "source":
            new_volume = self.current_volume - volume
        elif cmd[0] == "route":
            new_volume = self.current_volume
        elif cmd[0] == "sink":
            new_volume = self.current_volume + volume
        else:
            raise ValueError(f"Error! {self.__class__.__name__} {self.name} - Unknown command type {cmd[0]}.")

        if new_volume < 0 or new_volume > self.max_volume:
            self.logger.warning(f"Warning! New volume ({new_volume}) for {self.__class__.__name__} {self.name} outside 0-{self.max_volume} range. Truncating.")

        # truncate volume if out of range
        if new_volume < 0:
            self.current_volume = 0
        elif new_volume > self.max_volume:
            self.current_volume = self.max_volume
        else:
            self.current_volume = new_volume

        self.logger.debug(f"{self.__class__.__name__} {self.name} - Executing command {cmd}, transfer volume={volume} mL, new volume = {self.current_volume} mL.")


class ChemputerReactor(ChemputerFlask):
    def __init__(self, name, current_volume=0.0, max_volume=0.0, necks=1, **kwargs):
        super().__init__(name, current_volume, max_volume)

        self.necks = necks

    @property
    def capabilities(self):
        caps = []
        for port in range(self.necks):
            caps.extend([("source", port),
                         ("sink", port)])
        return caps


class ChemputerDispenserFlask(ChemputerFlask):
    """
    A chemical container that dispenses its contents
    by positive or negative displacement.
    """
    @property
    def capabilities(self):
        return [("sink", "in")]

    def execute(self, cmd, volume, **kwarg):
        # decrease volume even though we're sinking
        # dispensing/siphoning action is taking place
        self.current_volume -= 2 * volume
        super().execute(cmd, volume, **kwarg)


class ChemputerWaste(ChemputerFlask):
    @property
    def capabilities(self):
        return [("sink", 0)]


class ChemputerVacuum(ChemputerFlask):
    @property
    def capabilities(self):
        return [("sink", 0)]


class ChemputerCartridge(ChemputerFlask):
    @property
    def capabilities(self):
        return [("route", "in", "out")]


class ChemputerFilter(ChemputerFlask):
    @property
    def capabilities(self):
        return [("sink", "top"),
                ("sink", "bottom"),
                ("source", "bottom"),
                ("route", "top", "bottom")]


class ChemputerSeparator(ChemputerFlask):
    @property
    def capabilities(self):
        return [("sink", "top"),
                ("sink", "bottom"),
                ("source", "bottom"),
                ("route", "top", "bottom"),
                ("route", "bottom", "bottom")]

class ChemputerManifold(ChemputerFlask):
    @property
    def capabilities(self):
        return [("route", 0, 0)]
