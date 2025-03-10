from flask import Flask, session, g
from app.config import config
from app.extensions import db, migrate, ma, se
import os


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db_url = app.config.get('SQLALCHEMY_DATABASE_URI', 'No database URL configured')
    app.logger.info(f"Using database: {db_url}")

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    se.init_app(app)

    with app.app_context():
        from app.models import (
            Role, User, Category, Product,
            Order, OrderDetail, Feedback, ProductGallery, Permission
        )

    @app.before_request
    def load_logged_in_user():
        user_id = session.get('user_id')
        if user_id is None:
            g.user = None
        else:
            g.user = User.get_by_id(user_id)

    from app.routes.main import main
    app.register_blueprint(main)

    from app.routes.auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

    from app.routes.payment import payment
    app.register_blueprint(payment, url_prefix='/payment')

    from app.routes.admin import admin
    app.register_blueprint(admin, url_prefix='/admin')

    from app.utils.jinja_filters import register_filters
    register_filters(app)

    from app.commands import register_commands
    register_commands(app)
    register_error_handlers(app)

    app.permanent_session_lifetime = int(os.environ.get('SESSION_TIMEOUT', 86400))

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