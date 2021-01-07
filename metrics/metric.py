from loggable.loggable import Loggable
import psutil
import logging


class Metric(Loggable):
    """
    Class of a metric representing measurable parameters.
    Used for inheriting attributes and common methods.
    """

    def __init__(self, process: psutil.Process, command: str, iteration: int, subject: str, debug_logger: logging.Logger):
        super().__init__(command, iteration, subject, debug_logger)
        self.process = process

    def measure(self):
        pass

    def dump_to_file(self, path: str):
        pass

    def __str__(self):
        pass
