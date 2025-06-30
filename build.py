#!/usr/bin/env python3
from pathlib import Path
import shutil
import subprocess
import sys

def main():
    # Clean files from previous runs
    build_dir = Path('build')
    shutil.rmtree(build_dir, ignore_errors=True)
    # Create a new working copy
    src_dir = Path('src')
    ftlib_dir = build_dir / 'modules' / 'ftlib'
    shutil.copytree(src_dir, ftlib_dir)
    # Godot requires these specific files to be at the top level of the module
    files_to_move = [
        'config.py',
        'register_types.h',
        'SCsub'
    ]
    godot_adapter_dir = ftlib_dir / 'godot_adapter'
    for fname in files_to_move:
        src = godot_adapter_dir / fname
        dst = ftlib_dir / fname
        shutil.move(src, dst)
    # Run scons in godot directory
    pass_args = sys.argv[1:]
    godot_dir = Path('godot')
    if godot_dir.is_dir():
        subprocess.run(['scons', 'custom_modules=../build/modules'] + pass_args, cwd=godot_dir, check=True)

if __name__ == '__main__':
    main()