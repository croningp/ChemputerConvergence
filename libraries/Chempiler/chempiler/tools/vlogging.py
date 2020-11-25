"""
(c) 2019 The Cronin Group, University of Glasgow

This file contains all utilities required to record webcam videos at variable
frame rates, with time stamp, and the current INFO level log message overlaid.
"""

import cv2
import logging
import queue
import time


class VlogHandler(logging.Handler):
    """
    Logging module handler class. Inherits directly from the logging.Handler
    prototype, as no fancy stuff is required.
    """
    def __init__(self, queue=None):
        """
        Initialize the handler.

        Args:
            queue (queue.Queue): A queue object shared with the video recording
            process.
        """
        super().__init__()
        if queue:
            self.queue = queue
        else:
            raise Exception("ERROR: No queue object supplied!")

    def flush(self):
        """
        Empties the queue by popping all items until it's empty.
        """
        self.acquire()
        try:
            while not self.queue.empty():
                self.queue.get()
        finally:
            self.release()

    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then put into the queue.
        """
        try:
            msg = self.format(record)
            # print("Logger {0} is enqueuing \"{1}\"".format(self.name, msg))
            self.queue.put(msg)

        except Exception:
            self.handleError(record)


class RecordingSpeedFilter(logging.Filter):
    """
    Logging filter that only allows messages with logging level 5 to be passed
    on. Used for controlling video recording speed.
    """
    def filter(self, record):
        return record.levelno == 5


def recording_worker(
        message_queue, recording_speed_queue, video_path, camera_id):
    """
    Worker process which records a video to a file at variable frame rate. The
    main loop grabs an image from the camera, overlays a time stamp and the most
    recent log message, and then waits the appropriate time until the next frame
    is due. Log messages and requests to change recording speed are passed via
    queues. This worker is meant to be run as an individual process to improve
    performance in cPython.

    Args:
        message_queue (queue.Queue): A queue object containing logging messages.
        recording_speed_queue (queue.Queue): A queue object containing requests
                                             to change frame rate.
        video_path (str): A path to the output video file.
    """
    # constants for easy maintenance
    resolution = (1280, 720)
    fps = 24
    time_per_frame = 1 / fps

    # start capture
    cap = cv2.VideoCapture(camera_id)

    # set image size
    cv2.VideoCapture.set(cap, cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cv2.VideoCapture.set(cap, cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    # start video writer
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(video_path, fourcc, fps, resolution)

    # initialise working variables
    recording_speed = 1
    current_log_message = ""

    # keep recording
    while cap.isOpened():
        try:
            beginning_of_frame = time.time()
            ret, frame = cap.read()
            if ret:
                # create and format time stamp
                timestamp = time.localtime(beginning_of_frame)
                timestamp_pretty_print = time.strftime(
                    "%Y-%m-%d %H:%M:%S", timestamp)
                if recording_speed == "pause":
                    timestamp_string = f"{timestamp_pretty_print} (paused)"
                else:
                    timestamp_string = f"{timestamp_pretty_print}\
 {recording_speed}X"

                # check if there is a new log message, if there's more than one
                # discard all but the most recent one
                while not message_queue.empty():
                    current_log_message = message_queue.get()

                # insert time stamp and log message as overlay
                cv2.putText(
                    frame,
                    timestamp_string,
                    (10, 660),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA)
                cv2.putText(
                    frame,
                    current_log_message,
                    (10, 710),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA)

                # write the frame
                out.write(frame)

                # display video
                # cv2.imshow("frame", frame)
            else:
                break

            if recording_speed == "pause":
                # block until new recording speed requested
                recording_speed = recording_speed_queue.get()
            elif recording_speed == "stop":
                cap.release()
                out.release()
                cv2.destroyAllWindows()
                # terminate thread
                return 0
            else:  # recording speed is a number
                timeout = int(recording_speed) * time_per_frame
                try:
                    # block until the next frame due or new recording speed
                    # requested
                    recording_speed = recording_speed_queue.get(timeout=timeout)
                except queue.Empty:
                    # capture next frame
                    continue

        except EOFError:
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            return -1
