import logging
import sys


class Summary:
    """
    Class holding functionality of summary of the
    runner session.
    Return codes of each command are aggregated.
    A summary of frequencies and iterations
    can be printed and most frequent return code returned.
    """

    def __init__(self, debug_logger: logging.Logger):
        self.return_codes = []
        self.return_codes_frequencies = {}
        self.return_codes_iterations = {int: []}  # Dict of lists of iterations
        self.debug_logger = debug_logger

    def add_return_code(self, return_code: int):
        """
        Include a return code to the summary.
        :param return_code: return code to be added
        """
        self.return_codes.append(return_code)

    def print_summary(self):
        """
        Summarize current state of return codes and print the summary.
        """
        self.__make_analysis()
        self.debug_logger.debug('Printing summary of return codes')
        print('Summary:')
        for key in self.return_codes_frequencies:
            print(f'Return code: {key};'
                  f' Frequency: {self.return_codes_frequencies[key]};'
                  f' Iterations: {self.return_codes_iterations[key]}')

    def get_most_frequent(self):
        """
        Get the most frequent return code.
        :return: most frequent return code, or 1 if no return code was added.
        """
        return max(self.return_codes_frequencies, key=self.return_codes_frequencies.get) \
            if self.return_codes_frequencies else 1

    def summarize_and_exit(self):
        """
        Print the summary and exit with the most frequent return code.
        """
        self.print_summary()
        sys.exit(self.get_most_frequent())

    def __make_analysis(self):
        self.debug_logger.debug('Analyzing frequency of return codes')

        for index in range(len(self.return_codes)):
            current_return_code = self.return_codes[index]
            self.__aggregate_frequency(current_return_code)
            self.__add_iteration(current_return_code, index)

    def __aggregate_frequency(self, return_code):
        if return_code in self.return_codes_frequencies:
            self.return_codes_frequencies[return_code] += 1
        else:
            self.return_codes_frequencies[return_code] = 1

    def __add_iteration(self, return_code, index):
        if return_code in self.return_codes_iterations:
            self.return_codes_iterations[return_code].append(index)
        else:
            self.return_codes_iterations[return_code] = [index]
