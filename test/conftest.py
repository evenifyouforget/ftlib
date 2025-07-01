from pathlib import Path
import subprocess

def pytest_sessionstart(session):
    # build once the binary we will run for every test
    cli_adapter_dir = Path() / 'src' / 'cli_adapter'
    subprocess.run(['scons'], cwd=cli_adapter_dir, check=True)