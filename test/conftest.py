import pytest
from pathlib import Path
import subprocess

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