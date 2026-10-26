"""HEMS Application Factory."""
from flask import Flask, jsonify
from hems.config import Config
from hems.db import init_db_command


from flask.json.provider import DefaultJSONProvider
from datetime import date, datetime

class CustomJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, date):
            return o.isoformat()
        return super().default(o)

def create_app(test_config=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.json = CustomJSONProvider(app)
    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.from_mapping(test_config)
    if not app.config["TESTING"] and not app.config.get("SECRET_KEY"):
        raise RuntimeError("Set SECRET_KEY in the environment before starting HEMS.")

    app.cli.add_command(init_db_command)
    from hems.db import close_db, seed_demo_data_command
    app.teardown_appcontext(close_db)

    from hems.api.auth_routes import auth_bp
    from hems.api.appliance_routes import appliance_bp
    from hems.api.fuel_routes import fuel_bp
    from hems.api.analytics_routes import analytics_bp
    from hems.api.tariff_routes import tariff_bp
    from hems.web.routes import web_bp

    app.cli.add_command(seed_demo_data_command)
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(appliance_bp, url_prefix="/api/v1/appliances")
    app.register_blueprint(fuel_bp, url_prefix="/api/v1/fuel-logs")
    app.register_blueprint(analytics_bp, url_prefix="/api/v1/analytics")
    app.register_blueprint(tariff_bp, url_prefix="/api/v1/settings/tariffs")
    app.register_blueprint(web_bp)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"status": "error", "message": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    return app
