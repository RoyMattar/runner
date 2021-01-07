from metrics import metric
import logging
import psutil


class Network(metric.Metric):
    """
    Monitor network stats of a given process.
    """

    def __init__(self, process: psutil.Process, command: str, iteration: int, debug_logger: logging.Logger):
        super().__init__(process, command, iteration, str(self), debug_logger)
        self.io_counters_dicts: list = []
        self.connections_dicts: list = []

    def measure(self):
        """
        Perform the measurements as long as the process is running and is not a zombie.
        """
        self.debug_logger.debug(f'Measuring network stats of command {self.command} at iteration {self.iteration}')

        while self.process.is_running():
            # Challenge: access denied here if not using root
            connections_dict = self.process.connections()
            # _asdict() is protected but necessary for iterating using keys
            net_io_counters_dict = psutil.net_io_counters()._asdict()
            self.connections_dicts.append(connections_dict)
            self.io_counters_dicts.append(net_io_counters_dict)

            if self.process.status() == psutil.STATUS_ZOMBIE:
                break

    def dump_to_file(self):
        """
        Dump current measurements to a file.
        """
        self.debug_logger.debug(f'Dumping to file network stats of command {self.command}'
                                f' at iteration {self.iteration}')

        try:
            with open(self._get_log_path('log'), 'w') as fd:
                print('Connections:', file=fd)
                for index in range(len(self.connections_dicts)):
                    print(f'{index+1}: {self.connections_dicts[index]}', file=fd)

                print('\nNetwork IO:', file=fd)
                for index in range(len(self.io_counters_dicts)):
                    print(f'{index+1}: {self.io_counters_dicts[index]}', file=fd)

                if len(self.io_counters_dicts) > 0:
                    print(f'\nTotal network IO counters: {self.io_counters_dicts[len(self.io_counters_dicts) - 1]}',
                          file=fd)

        except EnvironmentError as e:
            print(e)

    def __str__(self):
        return 'network'
