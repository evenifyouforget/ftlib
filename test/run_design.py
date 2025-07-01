from collections import namedtuple
from pathlib import Path
import subprocess

RunDesignResult = namedtuple('RunDesignResult', ['proc', 'real_solve_ticks', 'real_end_ticks'])

def run_design(design_struct, max_ticks):
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
    return RunDesignResult(
        proc=proc,
        real_solve_ticks=real_solve_ticks,
        real_end_ticks=real_end_ticks,
        )