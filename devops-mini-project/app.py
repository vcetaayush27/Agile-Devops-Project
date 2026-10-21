"""Flask delivery demo. Run locally with python run.py, not Flask's debug server."""
import os
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        APP_VERSION=os.getenv("APP_VERSION", "local"),
        BUILD_TIME=os.getenv("BUILD_TIME", "Not recorded for local run"),
        MAX_CONTENT_LENGTH=16384,
    )
    if config:
        app.config.update(config)

    @app.get("/")
    def index():
        return render_template("index.html", version=app.config["APP_VERSION"],
                               build_time=app.config["BUILD_TIME"])

    @app.get("/health")
    def health():
        response = jsonify(status="ok", service="devops-mini-project",
                           version=app.config["APP_VERSION"],
                           time_utc=datetime.now(timezone.utc).isoformat())
        response.headers["Cache-Control"] = "no-store, max-age=0"
        return response

    @app.after_request
    def headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
            "base-uri 'self'; frame-ancestors 'none'"
        )
        if response.mimetype == "text/html":
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    return app


app = create_app()
