"""Loads the local E0 sample datasets and sessions."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    scripts = [
        ROOT / "data" / "northwind" / "load_northwind.py",
        ROOT / "data" / "sec_edgar" / "load_sec_edgar.py",
        ROOT / "data" / "bird" / "load_bird.py",
        ROOT / "data" / "sessions" / "build_sessions.py",
    ]
    for script in scripts:
        subprocess.run([sys.executable, str(script)], check=True)


if __name__ == "__main__":
    main()

