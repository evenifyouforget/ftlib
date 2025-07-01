import pytest
import itertools
from collections import namedtuple
import csv
import math
from pathlib import Path
import re
import subprocess
from get_design import retrieveLevel, retrieveDesign, designDomToStruct

SingleDesignData = namedtuple('SingleDesignData', ['design_uid', 'design_struct', 'expect_solve_ticks', 'design_max_ticks'])

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
        result.append(SingleDesignData(
            design_uid=design_uid,
            design_struct=design_struct,
            expect_solve_ticks=solve_ticks,
            design_max_ticks=design_max_ticks
            ))
    return result

# placeholder test
def f():
    raise SystemExit(1)


def test_mytest():
    with pytest.raises(SystemExit):
        f()

# another placeholder test
def add(a, b):
    return a + b

# Define the data for test case generation
test_data = [
    ((1, 2), 3),   # Input: (1, 2) | Expected Output: 3
    ((0, 0), 0),   # Input: (0, 0) | Expected Output: 0
    ((-1, 1), 0),  # Input: (-1, 1) | Expected Output: 0
]

# Define the pytest_generate_tests hook to generate test cases
def pytest_generate_tests(metafunc):
    if 'test_input' in metafunc.fixturenames:
        # Generate test cases based on the test_data list
        metafunc.parametrize('test_input,expected_output', test_data)
    if 'design_uid' in metafunc.fixturenames:
        metafunc.parametrize('design_uid,design_struct,expect_solve_ticks,design_max_ticks', generate_test_single_design_data())

# Define the actual test function
def test_addition(test_input, expected_output):
    result = add(*test_input)
    assert result == expected_output, f"Expected {expected_output}, but got {result}"

# test single designs
def test_single_design(design_uid, design_struct, global_max_ticks, expect_solve_ticks, design_max_ticks):
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
    # generate serialized input
    serialized_input = []
    serialized_input.append(max_ticks)
    all_pieces = design_struct.goal_pieces + design_struct.design_pieces + design_struct.level_pieces
    serialized_input.append(len(all_pieces))
    for i, piece_struct in enumerate(all_pieces):
        serialized_input.append(piece_struct.type_id)
        serialized_input.append(i)
        serialized_input.append(piece_struct.x)
        serialized_input.append(piece_struct.y)
        serialized_input.append(piece_struct.w)
        serialized_input.append(piece_struct.h)
        serialized_input.append(piece_struct.angle)
        joints = list(piece_struct.joints)
        joints += [-1] * (2 - len(joints))
        serialized_input += joints
    serialized_input.append(design_struct.build_area.x)
    serialized_input.append(design_struct.build_area.y)
    serialized_input.append(design_struct.build_area.w)
    serialized_input.append(design_struct.build_area.h)
    serialized_input.append(design_struct.goal_area.x)
    serialized_input.append(design_struct.goal_area.y)
    serialized_input.append(design_struct.goal_area.w)
    serialized_input.append(design_struct.goal_area.h)
    serialized_input = ' '.join(map(str, serialized_input))
    # run the executable
    exec_path = Path() / 'src' / 'cli_adapter' / 'run_single_design'
    proc = subprocess.run([exec_path], text=True, input=serialized_input, stdout=subprocess.PIPE)
    assert proc.returncode == 0
    stdout = proc.stdout
    real_solve_ticks, real_end_ticks = map(int, stdout.strip().split())
    correct_result_message = f'solves at {expect_solve_ticks}' if expect_solve_ticks is not None else f'still no solve within {design_max_ticks}'
    if expect_solve_ticks is None or expect_solve_ticks > real_end_ticks:
        # should not solve
        if real_solve_ticks != -1:
            raise AssertionError(f'Design solved at {real_solve_ticks} (expected: {correct_result_message})')
    else:
        # should solve
        if real_solve_ticks == -1:
            raise AssertionError(f'Design did not solve within {real_end_ticks} (expected: {correct_result_message})')
        if real_solve_ticks != expect_solve_ticks:
            raise AssertionError(f'Design solved at {real_solve_ticks} (expected: {correct_result_message})')