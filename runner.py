import sys
import psutil
from helper import args_parser
from subprocess import PIPE

EXIT_SUCCESS = 0


class Runner:
    def __init__(self,
                 command: str,
                 sys_trace=False,
                 call_trace=False,
                 log_trace=False,
                 net_trace=False):
        """
        :param command: command to run.
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

    def run(self):
        """
        Run a given command.
        """
        split_command = self.command.split()

        process = psutil.Popen(split_command, stdout=PIPE, stderr=PIPE, encoding='ascii')

        # Wait for command to finish executing and pick up stdout and stderr
        stdout, stderr = process.communicate()

        # Print outputs of the command
        print(stdout, file=sys.stdout)
        print(stderr, file=sys.stderr)

        # Get return code
        return_code = getattr(process, 'returncode')

        return return_code


if __name__ == "__main__":
    # Parse command line arguments
    args = args_parser.parse()

    # Keep track of the failed count
    current_failed_count = 0

    # Create the runner
    r = Runner(args.command,
               sys_trace=args.sys_trace,
               call_trace=args.call_trace,
               log_trace=args.log_trace,
               net_trace=args.net_trace)

    # Run session
    try:
        for i in range(args.count):

            current_return_code = r.run()

            if current_return_code != EXIT_SUCCESS:
                current_failed_count += 1

            if current_failed_count == args.failed_count:
                break

    except BaseException as e:
        print(e)
