"""Remove __pycache__ directories."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from shutil import rmtree


def remove_pycache(path: str) -> None:
    """Remove __pycache__ directories."""
    logging.info("Start removing __pycache__")
    for root, dirs, _ in os.walk(path):
        if "__pycache__" in dirs:
            pycache_path = Path(*(root, "__pycache__"))
            rmtree(pycache_path)
    logging.info("Done")


if __name__ == "__main__":
    remove_pycache(".")
