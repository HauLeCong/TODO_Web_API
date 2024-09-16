# %%
from flask import Flask
from api.config import create_config
import os


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    config = create_config(app)
    app.config.from_object(config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db

    db.init_app(app)

    from . import auth, todo

    app.register_blueprint(auth.bp)
    app.register_blueprint(todo.bp)

    @app.route("/hello")
    def hello():
        return "Hello"

    return app


app = create_app()

# %%
