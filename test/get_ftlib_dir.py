from pathlib import Path

def get_ftlib_dir() -> Path:
    return Path(__file__).resolve().parent.parent