from flask import Flask
from app.config import config
from app.extensions import db, migrate, ma
import os


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    with app.app_context():
        from app.models import (
            Role, User, Category, Product,
            Order, OrderDetail, Feedback, ProductGallery
        )

    from app.routes.main import main
    app.register_blueprint(main)

    from app.commands import register_commands
    register_commands(app)
    register_error_handlers(app)

    return app


def register_error_handlers(app):

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403


from flask import render_template