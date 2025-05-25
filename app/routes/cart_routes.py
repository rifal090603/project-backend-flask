from flask import Blueprint, jsonify, request, session
from flask_jwt_extended import jwt_required, get_jwt_identity  # Menggunakan JWT
from app.controllers import cart_controller
from app.models.cart_models import CartItem
from app.models.transaction import Transaction
from app import db  # pastikan db diimport untuk query

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

# View cart items (GET)
@cart_bp.route('/view', methods=['GET'])
@jwt_required()  
def view_cart():
    # Dapatkan user_id dari token JWT
    current_user_id = get_jwt_identity()

    cart_items = CartItem.query.filter_by(user_id=current_user_id).all()
    result = []
    for item in cart_items:
        result.append({
            'id': item.id,
            'quantity': item.quantity,
            'menu': {
                'id': item.menu.id,
                'nama': item.menu.nama,
                'harga': item.menu.harga
            }
        })
    return jsonify({'cart_items': result}), 200

# Add to cart (POST)
@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    current_user_id = get_jwt_identity()
    
    print("Token valid, user_id:", current_user_id)
    return cart_controller.add_to_cart(current_user_id) 

# Remove item from cart (DELETE)
@cart_bp.route('/remove/<string:menu_id>', methods=['DELETE'])
@jwt_required()  # Ganti dengan JWT
def remove_from_cart(menu_id):
    current_user_id = get_jwt_identity()
    try:
        cart_controller.remove_item_from_cart(menu_id, current_user_id)  # Pastikan menggunakan user_id
        return jsonify({'message': 'Item berhasil dihapus dari keranjang'}), 200
    except Exception as e:
        return jsonify({'message': 'Gagal menghapus item', 'error': str(e)}), 500

# Checkout (POST)
@cart_bp.route('/checkout', methods=['POST'])
@jwt_required()  # Ganti dengan JWT
def checkout():
    current_user_id = get_jwt_identity()
    return cart_controller.checkout(current_user_id) 

# Checkout Success (GET)
@cart_bp.route('/checkout-success/<string:transaction_id>', methods=['GET'])
@jwt_required()  # Ganti dengan JWT
def checkout_success(transaction_id):
    transaction = Transaction.query.get(transaction_id)

    if not transaction:
        return jsonify({'message': 'Transaksi tidak ditemukan'}), 404

    return jsonify({
        'client_name': transaction.client_name,
        'transaction_id': transaction.id,
        'total_amount': transaction.total_amount,
        'method': transaction.method
    })

# Payment page (GET)
@cart_bp.route('/payment/<string:transaction_id>', methods=['GET'])
@jwt_required()  # Ganti dengan JWT
def payment_page(transaction_id):
    return jsonify({
        'message': 'Silakan lakukan pembayaran ke DANA',
        'transaction_id': transaction_id
    })
