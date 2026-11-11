import os

from flask import Flask

SECRET_KEY_ERROR = (
    "SECRET_KEY is required when running with debug=False and testing=False.\n"
    "Set it via environment variable SECRET_KEY or in instance/config.py "
    "(SECRET_KEY = '...').\n"
)


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a placeholder that is only accepted in debug/testing mode
        SECRET_KEY="dev",
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    env_secret = os.environ.get("SECRET_KEY")
    if env_secret is not None:
        app.config["SECRET_KEY"] = env_secret

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
        # the environment variable takes precedence over the instance config
        if env_secret is not None:
            app.config["SECRET_KEY"] = env_secret
    else:
        # load the test config if passed in
        app.config.update(test_config)

    if not app.debug and not app.testing:
        secret = (app.config.get("SECRET_KEY") or "").strip()
        if secret in ("", "dev"):
            raise RuntimeError(SECRET_KEY_ERROR)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    @app.route("/hello")
    def hello():
        return "Hello, World!"

    # register the database commands
    from . import db

    db.init_app(app)

    # apply the blueprints to the app
    from . import auth
    from . import blog

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule("/", endpoint="index")

    return app
