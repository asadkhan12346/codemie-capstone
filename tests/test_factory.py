import pytest
from flask import Flask

from flaskr import SECRET_KEY_ERROR
from flaskr import create_app

PRODUCTION_CONFIG = {"TESTING": False, "DEBUG": False}


def test_config(monkeypatch):
    """Test create_app without passing test config."""
    monkeypatch.setenv("SECRET_KEY", "not-the-dev-key")
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_hello(client):
    response = client.get("/hello")
    assert response.data == b"Hello, World!"


@pytest.mark.parametrize("config", [{"TESTING": True}, {"DEBUG": True}])
def test_secret_key_allowed_in_debug_or_testing(monkeypatch, config):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    create_app(config)


@pytest.mark.parametrize("secret", [None, "", "   ", "dev"])
def test_secret_key_required_in_production_mode(monkeypatch, secret):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    config = dict(PRODUCTION_CONFIG)
    if secret is not None:
        config["SECRET_KEY"] = secret

    with pytest.raises(RuntimeError) as excinfo:
        create_app(config)

    assert str(excinfo.value) == SECRET_KEY_ERROR


def test_secret_key_from_env_allows_startup(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "from-the-environment")
    app = create_app(PRODUCTION_CONFIG)
    assert app.config["SECRET_KEY"] == "from-the-environment"


def test_secret_key_from_instance_config_allows_startup(monkeypatch, tmp_path):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setattr(Flask, "auto_find_instance_path", lambda self: str(tmp_path))
    (tmp_path / "config.py").write_text("SECRET_KEY = 'from-instance-config'\n")
    monkeypatch.setenv("FLASK_DEBUG", "0")

    app = create_app()
    assert app.config["SECRET_KEY"] == "from-instance-config"


def test_secret_key_env_overrides_instance_config(monkeypatch, tmp_path):
    monkeypatch.setenv("SECRET_KEY", "from-the-environment")
    monkeypatch.setattr(Flask, "auto_find_instance_path", lambda self: str(tmp_path))
    (tmp_path / "config.py").write_text("SECRET_KEY = 'from-instance-config'\n")
    monkeypatch.setenv("FLASK_DEBUG", "0")

    app = create_app()
    assert app.config["SECRET_KEY"] == "from-the-environment"
