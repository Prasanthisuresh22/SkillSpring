from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template

from config import Config
from extensions import csrf, db, login_manager, migrate


def create_app(config_class=Config):
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=str(Path(__file__).parent.parent / "templates"),
    )
    app.config.from_object(config_class)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    @app.context_processor
    def inject_template_helpers():
        return {"current_year": datetime.now().year}

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app import models
    from app.auth.routes import auth
    from app.main.routes import main

    app.register_blueprint(main)
    app.register_blueprint(auth)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(models.User, int(user_id))

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "skillspring"})

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    with app.app_context():
        db.create_all()

    return app
