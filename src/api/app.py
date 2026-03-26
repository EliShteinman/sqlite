from flask import Flask

from src.api.defaults_bp import defaults_bp
from src.api.options_bp import options_bp
from src.api.validation_bp import validation_bp
from src.api.visibility_bp import visibility_bp


def create_app() -> Flask:
    app = Flask(__name__)

    app.register_blueprint(options_bp, url_prefix="/options")
    app.register_blueprint(visibility_bp, url_prefix="/visibility")
    app.register_blueprint(defaults_bp, url_prefix="/defaults")
    app.register_blueprint(validation_bp, url_prefix="/validation")

    return app
