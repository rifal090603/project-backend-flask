from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user 
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin
from app.controllers import dashboard_controller
from app.controllers import menu_controller
from app.models.auth_models import User
from app.models.menu_models import Menu
from app import db

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# GET dashboard/
@dashboard_bp.route('/', methods=['GET'])
@cross_origin(origin='http://localhost:3000', supports_credentials=True)
@jwt_required()
def dashboard_main_app():
    data, error, status = dashboard_controller.dashboard_data()
    if error:
        return jsonify(error), status

    # Serialisasi manual agar bisa dijadikan JSON
    serialized_data = {
        'jumlah_menu': data['jumlah_menu'],
        'jumlah_user': data['jumlah_user'],
        'jumlah_transaksi': data['jumlah_transaksi'],
        'total_pendapatan': data['total_pendapatan'],
        # Cek apakah data['keranjang_aktif'] sudah berupa dictionary atau list objek
        'keranjang_aktif': [
            item.to_dict() if hasattr(item, 'to_dict') else item 
            for item in data['keranjang_aktif']
        ],
        'users': [user.to_dict() for user in data['users']],
        'admins': [admin.to_dict() for admin in data['admins']],
        'clients': [client.to_dict() for client in data['clients']],
        'transaksi': [tx.to_dict() for tx in data['transaksi']],
        'menus': [menu.to_dict() for menu in data['menus']],
    }

    return jsonify(serialized_data), status


# GET dashboard/users
@dashboard_bp.route('/users', methods=['GET'])
@cross_origin(origin='http://localhost:3000', supports_credentials=True)
@jwt_required()
def get_users_admin():
    admins, clients, error, status = dashboard_controller.get_user_data()
    if error:
        return jsonify(error), status
    return jsonify({
        'admins': [admin.to_dict() for admin in admins],
        'clients': [client.to_dict() for client in clients]
    }), status

# Delete user
@dashboard_bp.route('/users/<uuid:user_id>', methods=['DELETE'])
def delete_user_admin(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

# GET dashboard/transactions?tanggal=YYYY-MM-DD
@dashboard_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions_admin():
    tanggal = request.args.get('tanggal')
    return dashboard_controller.get_transaksi_data(tanggal)


@dashboard_bp.route('/create-menu', methods=['POST'])
@jwt_required()
@cross_origin(origins='http://localhost:3000', supports_credentials=True)
def create_menu_admin():
    # Ambil user_id dari JWT
    user_id = get_jwt_identity()

    if request.method == 'OPTIONS':
        return '', 200 

    # Cek apakah user_id tersedia dari JWT
    if not user_id:
        return {'message': 'Unauthorized'}, 401  

    # Panggil controller untuk membuat menu admin
    return menu_controller.create_menu()


# PUT update menu
@dashboard_bp.route('/edit-menu/<int:menu_id>', methods=['PUT'])
@jwt_required()
@cross_origin(origins='http://localhost:3000', supports_credentials=True)
def edit_menu_admin(menu_id):
    
    return menu_controller.update_menu(menu_id)

@dashboard_bp.route('/menus', methods=['GET'])
@jwt_required()
def get_menus():
    menus = Menu.query.all()
    data = [menu.to_dict() for menu in menus]  
    return jsonify({'menus': data}), 200


# DELETE dashboard/menu/<menu_id>
@dashboard_bp.route('/menu/<int:menu_id>', methods=['DELETE'])
@jwt_required()
def delete_menu_admin(menu_id):
    return menu_controller.delete_menu(menu_id)

# done order
@dashboard_bp.route('/transactions/<string:transaction_id>/complete', methods=['POST'])
@jwt_required()
def complete_order_admin(transaction_id):
    return dashboard_controller.complete_transaction(transaction_id)

# cancel order
@dashboard_bp.route('/transactions/<string:transaction_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order_admin(transaction_id):
    return dashboard_controller.cancel_transaction(transaction_id)

