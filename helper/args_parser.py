import argparse
import sys


class HelpAction(argparse.Action):
    """
    HelpAction class to be passed as action
    of argument --help. This is to customize
    --help to print onto stderr.
    """
    def __init__(self, option_strings, dest=argparse.SUPPRESS, default=argparse.SUPPRESS, msg=None):
        super().__init__(option_strings=option_strings, dest=dest, default=default, nargs=0, help=msg)

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help(file=sys.stderr)
        parser.exit()


def check_positive(value):
    """
    Check the value to be positive.
    This function will be passed as type
    to assert positive integers.
    :param value
    :return: value
    """
    l_value = int(value)
    if l_value <= 0:
        raise argparse.ArgumentTypeError(f'{l_value} is not a valid argument (not a positive integer)')
    return l_value


def parse():
    """
    Parse the command line arguments.
    :return: args object
    """
    # Create the parser
    parser = argparse.ArgumentParser(description='Run a given command with options',
                                     add_help=False)

    # Add the arguments
    parser.add_argument('command',
                        type=str,
                        metavar='command',
                        help='command to run')

    parser.add_argument('-c',
                        '--count',
                        dest='count',
                        type=check_positive,
                        default=1,
                        help='number of times to run the given command')

    parser.add_argument('-fc',
                        '--failed-count',
                        dest='failed_count',
                        type=check_positive,
                        help='number of allowed failed command invocation attempts before giving up')

    parser.add_argument('-st',
                        '--sys-trace',
                        dest='sys_trace',
                        action='store_true',
                        help='for each failed execution, create a log for each of the following values,'
                             ' measured during command execution: Disk IO; Memory; Processes/threads'
                             ' and cpu usage of the command; Network card package counters')

    parser.add_argument('-ct',
                        '--call-trace',
                        dest='call_trace',
                        action='store_true',
                        help='for each failed execution, create a log with all the system calls ran by the command')

    parser.add_argument('-lt',
                        '--log-trace',
                        dest='log_trace',
                        action='store_true',
                        help='for each failed execution, create logs of the command output (stdout, stderr)')

    parser.add_argument('-nt',
                        '--net-trace',
                        dest='net_trace',
                        action='store_true',
                        help='for each failed execution, create a pcap file with the network traffic'
                             ' during the execution')

    parser.add_argument('-d',
                        '--debug',
                        dest='debug',
                        action='store_true',
                        help='debug mode, show each instruction executed by the script')

    parser.add_argument('-h',
                        '--help',
                        action=HelpAction,
                        msg='print a usage message to stderr explaining how the script should be used')

    # Execute the parse_args() method
    l_args = parser.parse_args()

    return l_args
