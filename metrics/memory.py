from metrics import metric
import logging
import psutil


class Memory(metric.Metric):
    """
    Monitor memory stats of a given process.
    """

    def __init__(self, process: psutil.Process, command: str, iteration: int, debug_logger: logging.Logger):
        super().__init__(process, command, iteration, str(self), debug_logger)
        self.info_dicts: list = []
        self.percent: float = 0

    def measure(self):
        """
        Perform the measurements as long as the process is running and is not a zombie.
        """
        self.debug_logger.debug(f'Measuring memory stats of command {self.command} at iteration {self.iteration}')

        while self.process.is_running():
            # Challenge: access denied here if not using root
            # _asdict() is protected but necessary for iterating using keys
            mem_info_dict = self.process.memory_info()._asdict()
            self.info_dicts.append(mem_info_dict)
            self.percent += self.process.memory_percent() - self.percent

            if self.process.status() == psutil.STATUS_ZOMBIE:
                break

    def dump_to_file(self):
        """
        Dump current measurements to a file.
        """
        self.debug_logger.debug(f'Dumping to file memory stats of command {self.command} at iteration {self.iteration}')

        try:
            with open(self._get_log_path('log'), 'w') as fd:
                for index in range(len(self.info_dicts)):
                    print(f'{index+1}: {self.info_dicts[index]}', file=fd)

                if len(self.info_dicts) > 0:
                    print(f'\nTotal memory IO counters: {self.info_dicts[len(self.info_dicts) - 1]}',
                          file=fd)

                print(f'\nMemory utilization as percentage of total physical system memory: {self.percent}%', file=fd)

        except EnvironmentError as e:
            print(e)

    def __str__(self):
        return 'memory'
