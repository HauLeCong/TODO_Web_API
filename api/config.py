# %%
import os
from dotenv import load_dotenv
from flask import current_app


# %%
class Config:
    def init_app(self, app):
        load_dotenv(os.path.join(app.instance_path, ".env"))
        self.DATABASE = os.path.join(app.instance_path, "todo.sqlite")
        self.SECRET_KEY = os.environ.get("SECRET_KEY")
        self.JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
        self.JWT_EXPR_TIME = os.environ.get("JWT_EXPR_TIME")


def create_config(app):
    config = Config()
    config.init_app(app)
    return config


# %%
