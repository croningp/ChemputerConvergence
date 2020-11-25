import logging
import os

def get_logger(exp_name, output_dir):
    logger = logging.getLogger("chempiler")
    logger.setLevel(logging.INFO)
    # remove any default handlers, e.g. from Jupyter
    # see https://github.com/ipython/ipython/issues/8282
    logger.handlers = []

    # create file handler which logs all messages
    log_folder = os.path.join(output_dir, "log_files")
    os.makedirs(log_folder, exist_ok=True)

    # add the handlers to the loggers
    logger.addHandler(get_info_file_handler(log_folder, exp_name))
    logger.addHandler(get_debug_file_handler(log_folder, exp_name))
    logger.addHandler(get_console_handler())

    return logger

def get_file_formatter():
    return logging.Formatter(
        "%(asctime)s ; %(levelname)s ; %(module)s ; %(threadName)s ;\
 %(message)s")

def get_console_handler():
    # create console handler which logs all messages
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    console_formatter = logging.Formatter(
        "%(asctime)s ; %(module)s ; %(message)s")
    ch.setFormatter(console_formatter)
    return ch

def get_info_file_handler(log_folder, exp_name):
    info_fh = logging.FileHandler(
        filename=os.path.join(log_folder, "{0}_info.log".format(
            exp_name)))
    info_fh.setLevel(logging.INFO)
    info_fh.setFormatter(get_file_formatter())
    return info_fh

def get_debug_file_handler(log_folder, exp_name):
    debug_fh = logging.FileHandler(
        filename=os.path.join(log_folder, "{0}_debug.log".format(
            exp_name)))
    debug_fh.setLevel(logging.DEBUG)
    debug_fh.setFormatter(get_file_formatter())
    return debug_fh
