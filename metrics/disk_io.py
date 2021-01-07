from metrics import metric
import logging
import psutil


class DiskIO(metric.Metric):
    """
    Monitor disk IO stats of a given process.
    """

    def __init__(self, process: psutil.Process, command: str, iteration: int, debug_logger: logging.Logger):
        super().__init__(process, command, iteration, str(self), debug_logger)
        self.io_counters_dicts: list = []

    def measure(self):
        """
        Perform the measurements as long as the process is running and is not a zombie.
        """
        self.debug_logger.debug(f'Measuring disk IO of command {self.command} at iteration {self.iteration}')

        while self.process.is_running():
            # Challenge: access denied here if not using root
            # _asdict() is protected but necessary for iterating using keys
            pio_counters_dict = self.process.io_counters()._asdict()
            self.io_counters_dicts.append(pio_counters_dict)

            if self.process.status() == psutil.STATUS_ZOMBIE:
                break

    def dump_to_file(self):
        """
        Dump current measurements to a file.
        """
        self.debug_logger.debug(f'Dumping to file disk IO stats of command {self.command}'
                                f' at iteration {self.iteration}')

        try:
            with open(self._get_log_path('log'), 'w') as fd:
                for index in range(len(self.io_counters_dicts)):
                    print(f'{index+1}: {self.io_counters_dicts[index]}', file=fd)
                if len(self.io_counters_dicts) > 0:
                    print(f'\nTotal Disk IO counters: {self.io_counters_dicts[len(self.io_counters_dicts) - 1]}',
                          file=fd)

        except EnvironmentError as e:
            print(e)

    def __str__(self):
        return 'disk_io'
