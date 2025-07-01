import pytest
import itertools
from collections import namedtuple
import csv
import math
from pathlib import Path
import re
import subprocess
from get_design import retrieveLevel, retrieveDesign, designDomToStruct
from run_design import run_design

SingleDesignData = namedtuple('SingleDesignData', ['design_uid', 'design_struct', 'expect_solve_ticks', 'design_max_ticks', 'user_comment'])

def int_or_none(value):
    if value == '':
        return None
    return int(value)

def extract_design_id(link_or_id):
    matches = re.findall('(?:Id=)?(\\d+)', link_or_id)
    for match in matches:
        return int(match)
    return None

def generate_test_single_design_data():
    test_dir = Path() / 'test'
    fc_data_path = test_dir / 'fc_data.tsv'
    # read user submitted design info from sheet
    with open(fc_data_path, newline='') as file:
        reader = csv.reader(file, delimiter='\t')
        # tsv to 2D list
        fc_data = list(reader)
    # generate results
    result = []
    for row in fc_data:
        # parse row
        level_id, design_id, solve_ticks, design_max_ticks, user_comment, spectre_override, cpu_name, p2_solve_ticks, *_ = itertools.chain(row, [None]*10)
        level_id = extract_design_id(level_id)
        design_id = extract_design_id(design_id)
        solve_ticks = int_or_none(solve_ticks)
        design_max_ticks = int_or_none(design_max_ticks)
        # generate basic data
        design_uid = f'D{design_id}' if design_id else f'L{level_id}'
        # placeholder
        design_xml = retrieveDesign(design_id) if design_id else retrieveLevel(level_id)
        design_struct = designDomToStruct(design_xml)
        # build result tuple
        sdd = SingleDesignData(
            design_uid=design_uid,
            design_struct=design_struct,
            expect_solve_ticks=solve_ticks,
            design_max_ticks=design_max_ticks,
            user_comment=user_comment,
            )
        result.append((design_uid, sdd))
    return result

# Define the pytest_generate_tests hook to generate test cases
def pytest_generate_tests(metafunc):
    if 'design_uid' in metafunc.fixturenames:
        metafunc.parametrize('design_uid,design_data', generate_test_single_design_data())

# test single designs
def test_single_design(design_uid, design_data, global_max_ticks):
    # unpack tuple
    design_struct = design_data.design_struct
    expect_solve_ticks = design_data.expect_solve_ticks
    design_max_ticks = design_data.design_max_ticks
    user_comment = design_data.user_comment
    # calculate additional config
    max_ticks = math.inf
    if expect_solve_ticks:
        max_ticks = min(max_ticks, expect_solve_ticks + 100)
    if design_max_ticks:
        max_ticks = min(max_ticks, design_max_ticks)
    if global_max_ticks and global_max_ticks > 0:
        max_ticks = min(max_ticks, global_max_ticks)
    if max_ticks == math.inf:
        max_ticks = -1 # program treats -1 as infinity
    # run the design
    run_result = run_design(design_struct, max_ticks)
    # unpack result
    real_solve_ticks = run_result.real_solve_ticks
    real_end_ticks = run_result.real_end_ticks
    # check result
    correct_result_message = f'solves at {expect_solve_ticks}' if expect_solve_ticks is not None else f'still no solve within {design_max_ticks}'
    post_message = ''
    if user_comment:
        post_message += f' (user comment: {user_comment})'
    real_result_message = f'Design solved at {real_solve_ticks}' if real_solve_ticks != -1 else f'Design did not solve within {real_end_ticks}'
    error_message = f'{real_result_message} (expected: {correct_result_message}){post_message}'
    if expect_solve_ticks is None or expect_solve_ticks > real_end_ticks:
        # should not solve
        if real_solve_ticks != -1:
            raise AssertionError(error_message)
    else:
        # should solve
        if real_solve_ticks == -1:
            raise AssertionError(error_message)
        if real_solve_ticks != expect_solve_ticks:
            raise AssertionError(error_message)

# test memory safety
def test_valgrind(design_uid, design_data):
    # unpack tuple
    design_struct = design_data.design_struct
    # calculate additional config
    max_ticks = 100
    # run the design
    run_result = run_design(design_struct, max_ticks, command_prepend=['valgrind'])
    valgrind_report = run_result.proc.stderr
    if 'All heap blocks were freed -- no leaks are possible' not in valgrind_report:
        print(valgrind_report)
        raise AssertionError('Memory leaked when running design (see log)')