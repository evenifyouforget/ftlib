from pathlib import Path

# are we in the right directory?
def test_run_from_right_dir():
    test_dir = Path() / 'test' # intentionally not relative to the file
    assert test_dir.is_dir()
    conftest_path = test_dir / 'conftest.py'
    assert conftest_path.is_file()
