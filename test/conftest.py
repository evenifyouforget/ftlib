import datetime
import json
import pytest
from pathlib import Path
import re
import subprocess

# assign (probably) unique and sequential ID to current run
now = datetime.datetime.now(tz=datetime.timezone.utc)
current_run_uid = now.strftime('%Y-%m-%d-%H-%M-%S')

current_run_results = {}

# supported terminal colors, and at what pass rate we apply each color
pass_rate_colors = [
    ('red', 0),
    ('yellow', 0.5),
    ('green', 0.8),
    ('cyan', 0.95),
    ('blue', 1)
    ]

def fix_text_table_alignment(table):
    num_columns = max(map(len, table))
    for column_i in range(num_columns):
        max_len = max(len(row[column_i]) for row in table)
        for row in table:
            row[column_i] += ' ' * (max_len - len(row[column_i]))

def pytest_addoption(parser):
    parser.addoption("--all", action="store_true", help="Run all tests, and disable global tick limit. (slow)")
    parser.addoption("--max-ticks", type=int, default=None, help="Override max ticks limit per design. Has priority over --all")

@pytest.fixture(scope='session')
def global_max_ticks(pytestconfig):
    use_all = pytestconfig.getoption("--all")
    max_ticks_override = pytestconfig.getoption("--max-ticks")
    if max_ticks_override is not None:
        return max_ticks_override
    if use_all:
        return None
    return 2000

def pytest_sessionstart(session):
    # build once the binary we will run for every test
    cli_adapter_dir = Path() / 'cli_adapter'
    subprocess.run(['scons']) #TODO: add build option to only build cli adapter

def pytest_runtest_logreport(report):
    """
    Called after each test's setup, call, and teardown phase.
    We are interested in the 'call' phase for the actual test outcome.
    """
    if report.when == "call":
        # Extract the file path (e.g., test_example.py)
        file_path = report.nodeid.split("::")[0]

        # Extract the function name, stripping any parameter part
        function_name = report.nodeid.split("::")[-1]
        params = ''
        if '[' in function_name:
            function_name, params = function_name.split("[")
        params = params[:-1] # remove last ]
        design_key = re.search('[DL]\\d{6,8}', params)

        if design_key:
            # design acts as a unique key resistant to other internal changes
            params = design_key[0]

        if function_name not in current_run_results:
            current_run_results[function_name] = {}

        # will be "passed" or "failed" or "skipped"
        current_run_results[function_name][params] = report.outcome

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Add a section to the terminal summary report.
    This hook runs after all tests are complete and pytest's main summary is generated.
    You may still need to scroll up a bit to see the output.
    """
    # write results
    live_results_dir = Path() / 'test' / 'history' / 'live'
    live_results_dir.mkdir(parents=True, exist_ok=True)
    with open(live_results_dir / f'{current_run_uid}.json', 'w') as file:
        json.dump(current_run_results, file, indent=2, sort_keys=True)

    # get reference results if available
    reference_run_results = {}
    reference_run_dir = Path() / 'test' / 'history' / 'reference'
    reference_run_dir.mkdir(parents=True, exist_ok=True)
    reference_run_paths = sorted(reference_run_dir.glob('*.json'))
    if reference_run_paths:
        latest_reference_run_path = reference_run_paths[-1]
        with open(latest_reference_run_path) as file:
            reference_run_results = json.load(file)

    # title
    terminalreporter.write_sep("=", "pass rate grouped by function")
    # generate table
    table = []
    colors = []
    current_run_results_list = list(current_run_results.items())
    for function_name, per_test_results in current_run_results_list:
        # get pass/fail stats
        passed = 0
        failed = 0
        for params, result in per_test_results.items():
            passed += result == 'passed'
            failed += result == 'failed'
        total = passed + failed

        if total == 0:
            continue

        row = []
        row.append(function_name)

        pass_rate = passed / total
        row.append(f'{pass_rate:.2%}')
        row.append(f'({passed}/{total})')

        color = None
        for possible_color, required_pass_rate in pass_rate_colors:
            if pass_rate >= required_pass_rate:
                color = possible_color

        table.append(row)
        colors.append(color)

    fix_text_table_alignment(table)

    for color, row, (function_name, per_test_results) in zip(colors, table, current_run_results_list):
        settings = {color: True}
        terminalreporter.write_line(' '.join(row), **settings)

        # add regression table below
        ref_per_test_results = reference_run_results.get(function_name, {})
        pf_table = [[0] * 3 for _ in range(2)]
        for params, result in per_test_results.items():
            ref_result = ref_per_test_results.get(params, None)
            y = 0 if result == 'passed' else 1 if result == 'failed' else None
            x = 0 if ref_result == 'passed' else 1 if ref_result == 'failed' else 2
            if y is not None:
                pf_table[y][x] += 1
        regression_table = []
        regression_table.append(['Now \\ Ref', 'Pass', 'Fail', 'No data'])
        regression_table.append(['Pass'] + list(map(str, pf_table[0])))
        regression_table.append(['Fail'] + list(map(str, pf_table[1])))
        fix_text_table_alignment(regression_table)
        caused_regression = pf_table[1][0] != 0
        regression_color = 'red' if caused_regression else color
        for regression_row in regression_table:
            regression_settings = {color: True}
            terminalreporter.write_line(' '.join(regression_row), **regression_settings)
    
    # backend comparison between test_single_design (ftlib) and test_single_design_fcsim
    if 'test_single_design' in current_run_results and 'test_single_design_fcsim' in current_run_results:
        terminalreporter.write_sep("=", "backend comparison: ftlib vs fcsim")
        
        ftlib_results = current_run_results['test_single_design']
        fcsim_results = current_run_results['test_single_design_fcsim']
        
        # build comparison table
        backend_table = [[0] * 2 for _ in range(2)]
        all_params = set(ftlib_results.keys()) | set(fcsim_results.keys())
        
        for params in all_params:
            ftlib_result = ftlib_results.get(params, None)
            fcsim_result = fcsim_results.get(params, None)
            y = 0 if ftlib_result == 'passed' else 1 if ftlib_result == 'failed' else None
            x = 0 if fcsim_result == 'passed' else 1 if fcsim_result == 'failed' else None
            if y is not None and x is not None:
                backend_table[y][x] += 1
        
        comparison_table = []
        comparison_table.append(['ftlib \\ fcsim', 'Pass', 'Fail'])
        comparison_table.append(['Pass'] + list(map(str, backend_table[0])))
        comparison_table.append(['Fail'] + list(map(str, backend_table[1])))
        fix_text_table_alignment(comparison_table)
        
        # determine color based on backend agreement
        disagreements = backend_table[0][1] + backend_table[1][0]
        backend_color = 'green' if disagreements == 0 else 'yellow' if disagreements <= 2 else 'red'
        
        for comp_row in comparison_table:
            terminalreporter.write_line(' '.join(comp_row), **{backend_color: True})
