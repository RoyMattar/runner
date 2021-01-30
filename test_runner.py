import os
import re
import pytest
import psutil
import shutil
from subprocess import PIPE

LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')


@pytest.mark.parametrize(
    "command, count, expectation",
    [
        (f'dirname {__file__}', '1', os.path.abspath(os.path.curdir)),
        ('echo OK', '5', 'OK'),
    ])
def test_should_run_cmd_n_times_successfully_and_collect_its_output(command: str, count: str, expectation: str):
    p = psutil.Popen(['python', 'runner.py', command, '-c', count], stdout=PIPE, stderr=PIPE, encoding='ascii')
    stdout, stderr = p.communicate()
    out = str(stdout)
    err = str(stderr)
    assert len(err.strip()) == 0 and out.count(expectation) == int(count)


@pytest.mark.parametrize(
    "command, count, fails",
    [
        ('false', '5', '3'),
        ('ls zzz', '5', '3'),
    ])
def test_should_fail_n_times_out_of_m_and_exit(command: str, count: str, fails: str):
    p = psutil.Popen(['python', 'runner.py', command, '-c', count, '-fc', fails], stdout=PIPE, stderr=PIPE,
                     encoding='ascii')
    stdout, stderr = p.communicate()
    out = str(stdout)
    summary = re.search(rf'Return code: (.*); Frequency: (.*);', out).groups()
    assert summary[1] == fails


@pytest.mark.parametrize(
    "command, expectation",
    [
        ('false', 7),
    ])
def test_should_dump_log_files(command: str, expectation: int):
    shutil.rmtree(LOGS_DIR)
    p = psutil.Popen(['python', 'runner.py', command, '-lt', '-ct', '-st'])
    p.wait()

    num_of_files = 0
    for path, subdir, files in os.walk(LOGS_DIR):
        print(files)
        num_of_files += len(files)
    assert num_of_files == expectation
