"""Web Presentation Blueprint."""
from flask import Blueprint, render_template, send_from_directory

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def index():
    return render_template("index.html")


@web_bp.route("/favicon.ico")
def favicon():
    return send_from_directory(
        "static",
        "favicon.svg",
        mimetype="image/svg+xml",
    )
