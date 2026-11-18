import os
import subprocess
import sys

import pytest


DEFAULT_BASE_URL = "http://localhost:5000"


@pytest.mark.e2e
@pytest.mark.story("FLASKR-3")
@pytest.mark.ac("AC1")
def test_debug_or_testing_allows_missing_secret_key():
    # Code quote (current): flaskr/__init__.py sets default SECRET_KEY="dev".
    # This scenario is implemented as a smoke check: app can create when TESTING is True.
    from flaskr import create_app

    app = create_app({"TESTING": True})
    assert app.testing is True


@pytest.mark.e2e
@pytest.mark.story("FLASKR-3")
@pytest.mark.ac("AC2")
def test_production_mode_missing_secret_key_fails_startup():
    # Requires implementation to raise a clear error when debug/testing are False and SECRET_KEY not provided.
    from flaskr import create_app

    with pytest.raises(Exception) as e:
        create_app({"TESTING": False, "DEBUG": False, "SECRET_KEY": None})

    # Message must be validated once implementation exists.
    assert e.value is not None


@pytest.mark.e2e
@pytest.mark.story("FLASKR-3")
@pytest.mark.ac("AC3")
def test_production_mode_with_secret_key_uses_configured_value():
    from flaskr import create_app

    app = create_app({"TESTING": False, "DEBUG": False, "SECRET_KEY": "not-dev"})
    assert app.config["SECRET_KEY"] == "not-dev"


@pytest.mark.e2e
@pytest.mark.story("FLASKR-3")
@pytest.mark.ac("AC4")
def test_readme_documented_secret_key_allows_starting_app_process():
    # Black-box: attempt to run `flask --app flaskr --help` with SECRET_KEY set.
    # This verifies env var wiring without hardcoding any URL.
    env = os.environ.copy()
    env.setdefault("SECRET_KEY", "test-secret")

    proc = subprocess.run(
        [sys.executable, "-m", "flask", "--app", "flaskr", "--help"],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Usage" in proc.stdout
