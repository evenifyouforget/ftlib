import pytest
from pathlib import Path
import subprocess

# Count results per test function
# Key will be "file_path::function_name" just like pytest internals
test_function_results_aggregated = {}

def pytest_addoption(parser):
    parser.addoption("--all", action="store_true", help="Run all tests. (slow)")
    parser.addoption("--max-ticks", type=int, default=None, help="Override max ticks limit. Has priority over --all")

@pytest.fixture(scope='session')
def global_max_ticks(pytestconfig):
    use_all = pytestconfig.getoption("--all")
    max_ticks_override = pytestconfig.getoption("--max-ticks")
    if max_ticks_override is not None:
        return max_ticks_override
    if use_all:
        return None
    return 1000

def pytest_sessionstart(session):
    # build once the binary we will run for every test
    cli_adapter_dir = Path() / 'src' / 'cli_adapter'
    subprocess.run(['scons'], cwd=cli_adapter_dir, check=True)

def pytest_runtest_logreport(report):
    """
    Called after each test's setup, call, and teardown phase.
    We are interested in the 'call' phase for the actual test outcome.
    """
    if report.when == "call":
        # Extract the file path (e.g., test_example.py)
        file_path = report.nodeid.split("::")[0]

        # Extract the function name, stripping any parameter part
        function_name_with_params = report.nodeid.split("::")[-1]
        function_name = function_name_with_params.split("[")[0]

        # Create a unique key for the aggregated function (file + function name)
        aggregated_key = f"{file_path}::{function_name}"

        if aggregated_key not in test_function_results_aggregated:
            test_function_results_aggregated[aggregated_key] = {"passed": 0, "failed": 0, "skipped": 0}

        if report.outcome == "passed":
            test_function_results_aggregated[aggregated_key]["passed"] += 1
        elif report.outcome == "failed":
            test_function_results_aggregated[aggregated_key]["failed"] += 1
        # we don't care about skipped tests, but for completeness it's included
        elif report.outcome == "skipped":
            test_function_results_aggregated[aggregated_key]["skipped"] += 1

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Add a section to the terminal summary report.
    This hook runs after all tests are complete and pytest's main summary is generated.
    You may still need to scroll up a bit to see the output.
    """
    # title
    terminalreporter.write_sep("=", "pass rate grouped by function")
    # generate table
    table = []
    colors = []
    for aggregated_key, results in test_function_results_aggregated.items():
        # get pass/fail stats
        passed = results["passed"]
        failed = results["failed"]
        total = passed + failed

        if total == 0:
            continue

        row = []
        row.append(aggregated_key)

        pass_rate = passed / total
        row.append(f'{pass_rate:.2%}')
        row.append(f'({passed}/{total})')

        if failed == 0:
            color = 'green'
        elif pass_rate > 0.5:
            color = 'yellow'
        else:
            color = 'red'

        table.append(row)
        colors.append(color)

    # fix table alignment
    num_columns = max(map(len, table))
    for column_i in range(num_columns):
        max_len = max(len(row[column_i]) for row in table)
        for row in table:
            row[column_i] += ' ' * (max_len - len(row[column_i]))

    for color, row in zip(colors, table):
        settings = {color: True}
        terminalreporter.write_line(' '.join(row), **settings)