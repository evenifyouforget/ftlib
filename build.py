import os
import shutil
import subprocess

def main():
    # Clean files from previous runs
    shutil.rmtree('build', ignore_errors=True)
    # Create a new working copy
    shutil.copytree('src', 'build/modules/ftlib')
    # Godot requires these specific files to be at the top level of the module
    files_to_move = [
        'config.py',
        'register_types.h',
        'SCsub'
    ]
    for fname in files_to_move:
        src = os.path.join('build/modules/ftlib/godot_adapter', fname)
        dst = os.path.join('build/modules/ftlib', fname)
        if os.path.exists(src):
            shutil.move(src, dst)
    # Run scons in godot directory
    if os.path.isdir('godot'):
        subprocess.run(['scons', 'custom_modules=../build/modules'], cwd='godot', check=True)

if __name__ == "__main__":
    main()