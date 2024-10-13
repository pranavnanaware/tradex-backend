# app/__init__.py
import logging
from logging.handlers import RotatingFileHandler
import os

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from app.config import Config

from .extensions import db, jwt
from .utils.helpers import check_database_extensions
from .routes.stock import stock_bp
from .routes.auth import auth_bp
from .routes.trades import transactions_bp
from .routes.portfolio import portfolio_bp

migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app, resources={
        r"/*": {
            "origins": "http://localhost:3000",
            "supports_credentials": True
        }
    })
    app.config.from_object(config_class)
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_COOKIE_SAMESITE'] = 'Lax'

    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler(
            'logs/your_app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('YourApp startup')

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)  # Ensure this is correctly referencing Migrate

    with app.app_context():
        # Check database extensions
        check_database_extensions()

    app.register_blueprint(stock_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(transactions_bp, url_prefix='/api')
    app.register_blueprint(portfolio_bp, url_prefix='/api')

    return app
