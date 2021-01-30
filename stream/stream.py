from loggable.loggable import Loggable
from typing import IO
import logging


class Stream(Loggable):
    """
    Class representing a stream of data,
    which contents are available for file dump.
    """

    def __init__(self,
                 stream: IO,
                 stream_name: str,
                 command: str,
                 iteration: int,
                 debug_logger: logging.Logger):
        self.stream = stream
        self.stream_name = stream_name
        super().__init__(command, iteration, str(self), debug_logger)

    def dump_to_file(self):
        """
        Dump stream contents to a file.
        """
        self.debug_logger.debug(f'Dumping to file {self.stream_name} of command {self.command}'
                                f' at iteration {self.iteration}')

        try:
            extension = 'trace' if str(self) == 'strace' else 'log'
            with open(self._get_log_path(extension), 'w') as fd:
                print(self.stream, file=fd)

        except EnvironmentError as e:
            print(e)

    def __str__(self):
        return self.stream_name
