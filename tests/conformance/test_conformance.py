"""
Conformance test runner for vlang.

Discovers all `.vpl` files under `tests/conformance/programs/`, compiles
and runs them, and compares their actual stdout against the corresponding
`.expected` text files.

Run:
    pytest tests/conformance/test_conformance.py -v
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest
from conftest import run_vlang

# Detect toolchain availability
LLC_AVAILABLE = shutil.which("llc") is not None
GCC_AVAILABLE = shutil.which("gcc") is not None
CLANG_AVAILABLE = shutil.which("clang") is not None
CAN_COMPILE = (LLC_AVAILABLE and GCC_AVAILABLE) or CLANG_AVAILABLE

PROGRAMS_DIR = Path(__file__).parent / "programs"


def get_conformance_cases():
    """Return list of pytest.param objects discovered in the directory."""
    cases = []
    if not PROGRAMS_DIR.exists():
        return cases

    for root, _, files in os.walk(PROGRAMS_DIR):
        for f in files:
            if f.endswith(".vpl"):
                van_path = Path(root) / f
                # Look for either .expected or .expected.txt
                expected_path = van_path.with_suffix(".expected")
                if not expected_path.exists():
                    expected_path = van_path.with_suffix(".expected.txt")
                if expected_path.exists():
                    case_id = van_path.relative_to(PROGRAMS_DIR).as_posix()
                    marks = []
                    cases.append(pytest.param(van_path, expected_path, id=case_id, marks=marks))
    return sorted(cases, key=lambda p: p.id)


# Get test cases
CONFORMANCE_CASES = get_conformance_cases()


@pytest.mark.slow
@pytest.mark.skipif(not CAN_COMPILE, reason="Requires either (llc and gcc) or clang in PATH")
@pytest.mark.parametrize("van_path, expected_path", CONFORMANCE_CASES)
def test_conformance(van_path: Path, expected_path: Path, tmp_path: Path) -> None:
    """Compile a conformance source file to native binary, run it, and assert stdout."""
    # Write native binary to temporary directory
    binary_path = tmp_path / "prog"

    # Compile and link
    res = run_vlang("compile", str(van_path), "-o", str(binary_path), cwd=tmp_path)
    assert res.returncode == 0, f"Compilation failed: {res.stderr}\n{res.stdout}"

    # Run binary
    exec_res = subprocess.run(
        [str(binary_path)],
        capture_output=True,
        text=True,
    )

    # Read expected output
    expected_output = expected_path.read_text(encoding="utf-8")

    assert exec_res.stdout.strip() == expected_output.strip()
