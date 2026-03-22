"""
CLIs
"""
# src/pyhkts/_cli.py

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

TYPESHED = ROOT / "typeshed"
PYRIGHT_JS = ROOT / "pyright/packages/pyright/dist/pyright.js"


def pyright() -> None:
    """Convenience wrapper to run the custom pyright fork."""
    if not PYRIGHT_JS.exists():
        raise RuntimeError("Pyright is not built.")
    cmd = ["node", str(PYRIGHT_JS), "--typeshedpath", str(TYPESHED), *sys.argv[1:]]
    raise SystemExit(subprocess.call(cmd))
