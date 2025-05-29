from flask import Flask
from config import Config
from flask_cors import CORS
from app.extensions import db, migrate, jwt, socketio
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    # Konfigurasi tambahan
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY"),  # dari .env
        SESSION_COOKIE_SAMESITE='None',
        SESSION_COOKIE_SECURE=False,  # Ganti True di production (HTTPS)
    )

    # Inisialisasi ekstensi
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    socketio.init_app(app)
    CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

    # Register Blueprint
    from app.routes.menu_routes import menu_bp
    from app.routes.cart_routes import cart_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.command.create_admin import create_admin
    from app.routes.home_routes import home_bp
    from app.ml.capstone import ml_bp

    app.cli.add_command(create_admin)

    app.register_blueprint(menu_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(ml_bp)

    
    from app.socket import event

    return app
