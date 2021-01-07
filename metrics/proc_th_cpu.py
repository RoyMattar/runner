from metrics import metric
import logging
import psutil


class ProcThCpu(metric.Metric):
    """
    Monitor children processes, threads and
    CPU usage of a given process.
    """

    def __init__(self, process: psutil.Process, command: str, iteration: int, debug_logger: logging.Logger):
        super().__init__(process, command, iteration, str(self), debug_logger)
        self.children: list = []
        self.threads: tuple = ()
        self.cpu_times: tuple = ()
        self.cpu_percent_over_time: list = []
        self.cpu_num = self.process.cpu_num() if self.process.is_running() else None

    def measure(self):
        """
        Perform the measurements as long as the process is running and is not a zombie.
        """
        self.debug_logger.debug(f'Measuring processes, threads and CPU stats of command {self.command}'
                                f' at iteration {self.iteration}')

        while self.process.is_running():
            # Challenge: access denied here if not using root
            self.children = self.process.children()
            self.threads = self.process.threads()
            self.cpu_times = self.process.cpu_times()
            self.cpu_percent_over_time.append(self.process.cpu_percent())

            if self.process.status() == psutil.STATUS_ZOMBIE:
                break

    def dump_to_file(self):
        """
        Dump current measurements to a file.
        """
        self.debug_logger.debug(f'Dumping to file processes, threads and CPU stats of command {self.command}'
                                f' at iteration {self.iteration}')

        try:
            with open(self._get_log_path('log'), 'w') as fd:
                print('Children processes summary:', file=fd)
                print(self.children, file=fd)

                print('\nThreads summary:', file=fd)
                print(self.threads, file=fd)

                print('\nCPU times spent in modes:', file=fd)
                print(self.cpu_times, file=fd)

                print(f'\nCPU percent over time:', file=fd)
                print(self.cpu_percent_over_time, file=fd)

                print(f'\nCPU number: {self.cpu_num}', file=fd)

        except EnvironmentError as e:
            print(e)

    def __str__(self):
        return 'proc_th_cpu'
