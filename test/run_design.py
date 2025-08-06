from collections import namedtuple
from pathlib import Path
import shlex
import subprocess

RunDesignResult = namedtuple('RunDesignResult', ['proc', 'real_solve_ticks', 'real_end_ticks'])

def run_design(design_struct, max_ticks, command_prepend=None, command_append=None, backend='ftlib'):
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
    if backend == 'fcsim':
        base_dir = Path()
        exec_path = base_dir / 'fcsim' / 'run_single_design'
    else:
        exec_path = Path().parent.parent / 'bin' / 'run_single_design'
    command_prepend = command_prepend or []
    command_append = command_append or []
    command = command_prepend + [exec_path] + command_append
    proc = subprocess.run(command, text=True, input=serialized_input, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        debug_command_text = shlex.join(map(str, command))
        raise AssertionError(f'Process {debug_command_text} exited with return code {proc.returncode}')
    stdout = proc.stdout
    real_solve_ticks, real_end_ticks = map(int, stdout.strip().split())
    return RunDesignResult(
        proc=proc,
        real_solve_ticks=real_solve_ticks,
        real_end_ticks=real_end_ticks,
        )