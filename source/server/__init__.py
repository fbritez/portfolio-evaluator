from flask import Flask
from flasgger import Swagger

from source.database import init_db


def create_app():
    app = Flask(__name__)
    init_db()

    Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "Portfolio API",
            "description": "API to manage portfolio names and ticker lists in SQLite",
            "version": "1.0.0"
        },
        "basePath": "/api"
    })

    from .routes import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
