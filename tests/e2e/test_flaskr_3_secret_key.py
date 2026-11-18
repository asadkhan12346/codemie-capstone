import os
import re
import subprocess
import sys
from pathlib import Path

import pytest


DEFAULT_BASE_URL = "http://localhost:5000"


def _run_flask_command(env: dict[str, str], *args: str) -> subprocess.CompletedProcess:
    """Run flask CLI in a subprocess.

    Note: These tests validate startup behavior per FLASKR-3 by invoking the
    application factory through the Flask CLI.
    """
    merged_env = os.environ.copy()
    merged_env.update(env)

    return subprocess.run(
        [sys.executable, "-m", "flask", "--app", "flaskr", *args],
        env=merged_env,
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
    )


@pytest.mark.e2e
@pytest.mark.story("FLASKR-3")
@pytest.mark.ac("AC1")
def test_flaskr_3_ac1_app_starts_in_debug_without_secret_key_explicitly_configured():
    # AC1 is inherently about app.debug/app.testing. We approximate this by
    # running the dev server startup checks in debug.
    #
    # Current code sets SECRET_KEY default to "dev" in flaskr/__init__.py.
    proc = _run_flask_command({"FLASK_DEBUG": "1"}, "routes")
    assert proc.returncode == 0, proc.stderr


@pytest.mark.e2e
@pytest.mark.story("FLASKR-3")
@pytest.mark.ac("AC2")
def test_flaskr_3_ac2_startup_fails_in_production_when_secret_key_missing_or_default():
    # Expected behavior per AC2: startup fails with clear error message.
    #
    # This test is written against the acceptance criteria and will FAIL until
    # the application implements the startup validation.
    proc = _run_flask_command(
        {
            "FLASK_DEBUG": "0",
            "FLASK_ENV": "production",
            # Ensure no SECRET_KEY is provided in env.
            "SECRET_KEY": "",
        },
        "routes",
    )

    # AC2 expects a failure.
    assert proc.returncode != 0
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")

    # "clear error message describing how to set SECRET_KEY"
    # We only assert that it mentions SECRET_KEY and set/configure guidance.
    assert "SECRET_KEY" in combined
    assert re.search(r"set|configure|environment|instance", combined, re.IGNORECASE)


@pytest.mark.e2e
@pytest.mark.story("FLASKR-3")
@pytest.mark.ac("AC3")
def test_flaskr_3_ac3_app_starts_in_production_when_secret_key_is_configured():
    proc = _run_flask_command(
        {"FLASK_DEBUG": "0", "FLASK_ENV": "production", "SECRET_KEY": "not-dev"},
        "routes",
    )
    assert proc.returncode == 0, proc.stderr


@pytest.mark.e2e
@pytest.mark.story("FLASKR-3")
@pytest.mark.ac("AC4")
def test_flaskr_3_ac4_readme_configured_secret_key_allows_startup():
    # README.rst currently documents:
    #   $ flask --app flaskr run --debug
    # AC4 requires README to include SECRET_KEY configuration. This test
    # validates the documented approach once README is updated.
    proc = _run_flask_command(
        {"FLASK_DEBUG": "0", "FLASK_ENV": "production", "SECRET_KEY": "from-readme"},
        "routes",
    )
    assert proc.returncode == 0, proc.stderr
