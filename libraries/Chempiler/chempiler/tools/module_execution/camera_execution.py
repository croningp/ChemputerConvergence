"""
(c) 2019 The Cronin Group, University of Glasgow

This class provides a method to change the frame rate of a video log which may
or may be recorded. This is accomplished by logging messages at a level below
DEBUG containing the requested recording speed (in multiples of real time). The
beauty of this approach is that a) most of the complicated message passing is
handled by the logging module, and b) if no recording is running, the workings
of this module are entirely without consequence because all other loggers reject
this level.
"""

import logging


class CameraExecutioner(object):
    """
    Class to change camera recording speed

    TODO: add try/except statements to catch calls to unsupported methods!
    """
    def __init__(self):
        """
        Initialiser for the CameraExecutioner class
        """
        self.logger = logging.getLogger("main_logger.camera_logger")
        self.logger.setLevel(5)

    def change_recording_speed(self, recording_speed):
        """
        Method to change the camera recording speed. This method simply logs a
        message at level 5 (below DEBUG), which may or may not be intercepted by
        an appropriate vlogging handler.

        Args:
            recording_speed (int): Requested recording speed (in multiples of
            real time speed)
        """
        # store recording speed; used in `resume`
        self.recording_speed = recording_speed
        self.logger.log(level=5, msg=recording_speed)

    def pause(self):
        """
        Pause video recording. The current recording speed is stored to be
        used when `resume` is called.
        """
        self.logger.log(level=5, msg="pause")

    def resume(self):
        """
        Resume video recording using last used recording speed.
        """
        self.change_recording_speed(self.recording_speed)

    def stop(self):
        """
        Stops video recording. Recording cannot be restarted without restarting
        the chempiler.
        """
        self.logger.log(level=5, msg="stop")
