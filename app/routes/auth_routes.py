from flask import Blueprint
from app.controllers import auth_controller

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register_user():
    return auth_controller.register_user()

@auth_bp.route('/register-admin', methods=['POST'])
def register_admin():
    return auth_controller.register_admin()

@auth_bp.route('/login', methods=['POST'])
def login_user():
    return auth_controller.login_user_controller()

