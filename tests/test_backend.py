import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"


def load_tests(loader, standard_tests, pattern):
    sys.path.insert(0, str(BACKEND_DIR))
    return loader.discover(
        start_dir=str(BACKEND_DIR / "tests"),
        top_level_dir=str(BACKEND_DIR),
    )
