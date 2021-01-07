from abc import ABC
import os
import logging
from datetime import datetime

TIMESTAMP = str(datetime.now().timestamp())
LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../logs', TIMESTAMP)


class Loggable(ABC):
    """
    Class of a loggable object.
    Used for inheriting attributes and a common method.
    """

    def __init__(self, command: str, iteration: int, subject: str, debug_logger: logging.Logger):
        """
        :param command: command ran.
        :param iteration: iteration number if command is ran multiple times.
        :param subject: subject of the log.
        :param debug_logger: for print debugging.
        """
        self.command = command
        self.iteration = iteration
        self.subject = subject
        self.debug_logger = debug_logger

    def dump_to_file(self):
        pass

    def __str__(self):
        pass

    def _get_log_path(self, extension='log'):
        """
        Build path to log file out of identifying parameters and a timestamp.
        A directory named <TIMESTAMP> is created if it is not present, to store
        all the log files pertaining to the same timestamp.
        :param extension: extension of log file.
        :return: path as string.
        """
        self.__ensure_dir()
        command_name = self.command.split()[0]
        return os.path.join(LOGS_DIR, f'{command_name}_{self.iteration}_{self.subject}.{extension}')

    def __ensure_dir(self):
        self.debug_logger.debug(f'Creating directory {LOGS_DIR}')
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
            self.debug_logger.debug(f'Directory {LOGS_DIR} created')
