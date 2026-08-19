import logging

from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

from source.database import get_backend_name, init_db


def create_app():
    app = Flask(__name__)

    # Ensure root logger is configured so module-level loggers (logging.getLogger(__name__))
    # propagate to a console handler even when the app is imported (not run via app.py).
    root = logging.getLogger()
    if not root.handlers:
        root.setLevel(logging.INFO)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        root.addHandler(stream_handler)

    # Make sure Flask's app logger also has a handler and doesn't duplicate output
    app.logger.setLevel(logging.INFO)
    if not app.logger.handlers:
        app.logger.addHandler(stream_handler)

    # Ensure werkzeug (the HTTP server) logs are visible
    werk = logging.getLogger('werkzeug')
    werk.setLevel(logging.INFO)
    if not werk.handlers:
        werk.addHandler(stream_handler)

    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
    init_db()
    app.logger.info("Application initialized with %s database", get_backend_name())

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
