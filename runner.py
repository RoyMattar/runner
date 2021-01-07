import sys
import psutil
import logging
import signal
from helper import args_parser
from summary.summary import Summary
from subprocess import PIPE
from loggable.loggable import TIMESTAMP
from metrics.disk_io import DiskIO
from metrics.memory import Memory
from metrics.proc_th_cpu import ProcThCpu
from metrics.network import Network
from stream.stream import Stream

EXIT_SUCCESS = 0


class Runner:
    def __init__(self,
                 command: str,
                 debugger: logging.Logger,
                 sys_trace=False,
                 call_trace=False,
                 log_trace=False,
                 net_trace=False):
        """
        :param command: command to run.
        :param debugger: loggable object for debugging.
        :param sys_trace: if True, system measurements will be performed and dumped to files if command fails.
        :param call_trace: if True, system calls will be monitored and dumped to file if command fails.
        :param log_trace: if True, stdout and stderr of the command will be dumped to files if command fails.
        :param net_trace: if True, pcap file with the network traffic during the execution will be created.
        :return: return code of the command.
        """
        self.command = command
        self.sys_trace = sys_trace
        self.call_trace = call_trace
        self.log_trace = log_trace
        self.net_trace = net_trace
        self.debugger = debugger

    def run(self, iteration: int):
        """
        Run a given command.
        :param iteration: iteration number, if running the command multiple time. This is for debugging and logging.
        """
        split_command = self.command.split()

        self.debugger.debug(f'Forking a child process to run the command \"{self.command}\"')
        process = psutil.Popen(split_command, stdout=PIPE, stderr=PIPE, encoding='ascii')

        # Initialize system metrics objects
        metrics = [DiskIO(process, self.command, iteration, self.debugger),
                   Memory(process, self.command, iteration, self.debugger),
                   ProcThCpu(process, self.command, iteration, self.debugger),
                   Network(process, self.command, iteration, self.debugger)]

        # Continually perform system measurements
        for metric in metrics:
            metric.measure()

        # Create strace file using strace process
        # Challenge: some calls might get missed out because of race
        self.debugger.debug('Creating strace file')
        strace_command = f'strace -f -p {process.pid}'
        self.debugger.debug(f'Running command {strace_command}')
        strace = psutil.Popen(strace_command.split(), stdout=PIPE, encoding='ascii')

        # Wait for command to finish executing and pick up stdout and stderr
        self.debugger.debug('Waiting for child process to terminate in order to retrieve the stream outputs')
        stdout, stderr = process.communicate()

        # Print outputs of the command
        print(stdout, file=sys.stdout)
        print(stderr, file=sys.stderr)

        # Get return code
        return_code = getattr(process, 'returncode')
        self.debugger.debug(f'Command \"{self.command}\" of iteration {iteration} returned with code: {return_code}')

        # Pass Ctrl+C to strace process and get output
        self.debugger.debug('Passing Ctrl+C to strace')
        strace.send_signal(signal.SIGINT)

        # Get strace output
        strace_out = strace.communicate()

        # If command fails, create log files
        if return_code != EXIT_SUCCESS:

            if self.sys_trace:
                for metric in metrics:
                    metric.dump_to_file()

            if self.call_trace:
                strace_stream = Stream(strace_out, 'strace', self.command, iteration, self.debugger)
                strace_stream.dump_to_file()

            if self.log_trace:
                streams = [Stream(stdout, 'stdout', self.command, iteration, self.debugger),
                           Stream(stderr, 'stderr', self.command, iteration, self.debugger)]
                for stream in streams:
                    stream.dump_to_file()

        return return_code


def __exit_gracefully(signum, frame):
    """
    Redirected handler for SIGINT signal.
    This is for printing the summary even if
    Ctrl+C or 'kill' are passed.
    :param signum
    :param frame
    """

    # Restore the original signal handler in case Ctrl+C or 'kill' are passed again before exiting
    signal.signal(signal.SIGINT, original_sigint)
    signal.signal(signal.SIGINT, original_sigterm)

    try:
        debug_logger.debug('SIGINT caught.')
        summary.summarize_and_exit()

    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == "__main__":
    # Init debug loggable
    logging.basicConfig()
    debug_logger = logging.getLogger(__name__)

    # Init the summary object
    summary = Summary(debug_logger)

    # Redirect signals in order to print summary after Ctrl+C or 'kill'
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, __exit_gracefully)
    original_sigterm = signal.getsignal(signal.SIGTERM)
    signal.signal(signal.SIGTERM, __exit_gracefully)

    # Parse command line arguments
    args = args_parser.parse()

    if args.debug:
        # Turn debugging on
        debug_logger.setLevel(logging.DEBUG)

    debug_logger.debug(f'Timestamp: {TIMESTAMP}')
    debug_logger.debug(f'Command: {args.command}; Count: {args.count}; Failed count: {args.failed_count};'
                       f' Sys-trace: {args.sys_trace}; Call-trace: {args.call_trace}; Log-trace: {args.log_trace}')

    # Keep track of the failed count
    current_failed_count = 0

    # Create the runner
    r = Runner(args.command,
               debugger=debug_logger,
               sys_trace=args.sys_trace,
               call_trace=args.call_trace,
               log_trace=args.log_trace,
               net_trace=args.net_trace)

    # Run session
    try:
        for i in range(args.count):
            debug_logger.debug(f'Attempt {i + 1} out of {args.count} to run given command')

            current_return_code = r.run(i)

            summary.add_return_code(current_return_code)

            if current_return_code != EXIT_SUCCESS:
                current_failed_count += 1

            if current_failed_count == args.failed_count:
                break

        summary.summarize_and_exit()

    except BaseException as e:
        print(e)
