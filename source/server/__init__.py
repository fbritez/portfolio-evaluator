import logging

from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

from source.database import get_backend_name, init_db


def create_app():
    app = Flask(__name__)
    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
    init_db()
    logging.info("Application initialized with %s database", get_backend_name())

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
