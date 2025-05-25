from flask import Blueprint, request, jsonify
from app.models.menu_models import Menu
from app.controllers.menu_controller import get_all_menu
from flask_jwt_extended import jwt_required, get_jwt_identity  
from flask_cors import cross_origin

menu_bp = Blueprint('menu', __name__, url_prefix='/menu')

# GET
@menu_bp.route('/', methods=['GET'], strict_slashes=False)
@cross_origin(supports_credentials=True)
@jwt_required()
def menampilkan_menu():
    return get_all_menu()


# GET /api/menu/<id>
@menu_bp.route('/<int:menu_id>', methods=['GET'])
@jwt_required()  
def get_menu_id(menu_id):
    menu = Menu.query.get(menu_id)
    if menu:
        return jsonify(menu.to_dict()), 200
    else:
        return jsonify({'error': 'Menu tidak ditemukan'}), 404

# GET /api/menu/search?query=espresso
@menu_bp.route('/search', methods=['GET'])
@jwt_required()  
def search():
    query = request.args.get('query')
    if query:
        products = Menu.query.filter(Menu.nama.ilike(f'%{query}%')).all()
    else:
        products = []

    return jsonify([menu.to_dict() for menu in products]), 200
 