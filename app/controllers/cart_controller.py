from flask import request, jsonify
from app.models.cart_models import CartItem
from app.models.transaction import Transaction
from app.models.transaction_item import TransactionItem
from app.models.menu_models import Menu
from sqlalchemy.orm import joinedload
from datetime import datetime
from app.models.auth_models import User
from app import db
import uuid

def add_to_cart(user_id):
    data = request.get_json()
    menu_id = data.get('menuId')
    quantity = data.get('quantity')
    print(f"Received data: {data}")
    
    if not menu_id or not quantity:
        return jsonify({'message': 'Menu ID dan quantity wajib diisi'}), 400

    if quantity <= 0:
        return jsonify({'message': 'Jumlah quantity tidak valid'}), 400

    # Cek apakah menu ada di database
    menu = Menu.query.get(menu_id)
    if not menu:
        return jsonify({'message': 'Menu tidak ditemukan'}), 404

    # Cek apakah stock mencukupi
    if menu.stock < quantity:
        return jsonify({'message': 'Stock tidak mencukupi'}), 400

    # Cek apakah user ada di database
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User tidak ditemukan'}), 404

    # Kurangi stok menu
    menu.stock -= quantity

    try:
        # Simpan perubahan stok dan item ke keranjang
        db.session.add(CartItem(
            id=str(uuid.uuid4()),
            menu_id=menu_id,
            quantity=quantity,
            user_id=user_id
        ))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500

    return jsonify({'message': 'Berhasil ditambahkan ke keranjang'}), 201

# Hapus dari keranjang
def remove_item_from_cart(menu_id, user_id):
    item = CartItem.query.filter_by(menu_id=menu_id, user_id=user_id).first()

    if item:
        menu = Menu.query.get(item.menu_id)
        if menu:
            menu.stock += item.quantity

        db.session.delete(item)
        db.session.commit()

    return jsonify({'message': 'Item berhasil dihapus'}), 200

# Checkout
def checkout(user_id):
    data = request.get_json()

    client_name = data.get('client_name', '').strip()
    alamat = data.get('alamat', '').strip()
    no_meja = data.get('no_meja', '').strip()
    phone_number = data.get('phone_number', '').strip()
    order_type = data.get('order_type', '').strip().lower()
    pickup_date = data.get('pickup_date', '').strip()
    pickup_time = data.get('pickup_time', '').strip()
    payment_method = data.get('payment_method', '').strip().lower()

    # Validasi dasar
    if not client_name:
        return jsonify({'message': 'Nama client wajib diisi'}), 400

    if order_type not in ['dine-in', 'delivery', 'takeaway']:
        return jsonify({'message': 'Tipe pesanan tidak valid'}), 400

    if payment_method not in ['dana', 'tunai']:
        return jsonify({'message': 'Metode pembayaran tidak valid'}), 400

    pickup_datetime = None

    if order_type == 'dine-in':
        if not no_meja:
            return jsonify({'message': 'Nomor meja wajib diisi untuk dine-in'}), 400
        # dine-in boleh dana atau tunai, tidak perlu validasi khusus payment_method

    elif order_type == 'delivery':
        if not phone_number:
            return jsonify({'message': 'Nomor WhatsApp wajib diisi untuk delivery'}), 400
        if not alamat:
            return jsonify({'message': 'Alamat wajib diisi untuk delivery'}), 400
        # Untuk delivery, pickup_date dan pickup_time tidak wajib karena pengiriman, tapi bisa kamu sesuaikan
        # Jika memang butuh pickup_datetime, aktifkan validasi di bawah ini, jika tidak bisa dihapus:
        # if not pickup_date or not pickup_time:
        #     return jsonify({'message': 'Tanggal dan jam ambil wajib diisi untuk delivery'}), 400
        # else:
        #     try:
        #         pickup_datetime = datetime.strptime(f"{pickup_date} {pickup_time}", "%Y-%m-%d %H:%M")
        #     except ValueError:
        #         return jsonify({'message': 'Format tanggal/waktu pengambilan tidak valid'}), 400
        
        if payment_method != 'dana':
            return jsonify({'message': 'Metode pembayaran untuk delivery harus DANA'}), 400

    elif order_type == 'takeaway':
        if not phone_number:
            return jsonify({'message': 'Nomor WhatsApp wajib diisi untuk takeaway'}), 400
        if not pickup_date or not pickup_time:
            return jsonify({'message': 'Tanggal dan jam ambil wajib diisi untuk takeaway'}), 400
        try:
            pickup_datetime = datetime.strptime(f"{pickup_date} {pickup_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            return jsonify({'message': 'Format tanggal/waktu pengambilan tidak valid'}), 400
        
        if payment_method != 'dana':
            return jsonify({'message': 'Metode pembayaran untuk takeaway harus DANA'}), 400

    # Ambil cart
    cart_items = CartItem.query.options(joinedload(CartItem.menu)).filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({'message': 'Keranjang kosong'}), 400

    # Hitung total dan validasi stok
    total = 0
    for item in cart_items:
        if not item.menu or item.menu.stock < item.quantity:
            return jsonify({'message': f'Stok untuk menu {item.menu.nama} tidak cukup'}), 400
        total += item.menu.harga * item.quantity

    # Simpan transaksi
    transaction = Transaction(
        id=str(uuid.uuid4()),
        user_id=user_id,
        client_name=client_name,
        phone_number=phone_number if phone_number else None,
        order_type=order_type,
        alamat=alamat if order_type == 'delivery' else None,
        no_meja=no_meja if order_type == 'dine-in' else None,
        pickup_datetime=pickup_datetime,
        payment_method=payment_method,
        total_amount=total,
        status='pending_payment',
        is_verified=False,
        created_at=datetime.utcnow()
    )

    db.session.add(transaction)
    db.session.flush()  # Untuk dapatkan ID transaksi

    items_response = []
    for item in cart_items:
        trans_item = TransactionItem(
            transaction_id=transaction.id,
            menu_id=item.menu.id,
            product_name=item.menu.nama,
            quantity=item.quantity,
            price=item.menu.harga
        )
        db.session.add(trans_item)
        db.session.delete(item)  # Hapus dari cart

        items_response.append({
            'product_name': item.menu.nama,
            'quantity': item.quantity,
            'price': item.menu.harga
        })

    db.session.commit()

    return jsonify({
        'message': 'Checkout berhasil',
        'transaction_id': transaction.id,
        'total_amount': total,
        'order_type': order_type,
        'payment_method': payment_method,
        'pickup_datetime': pickup_datetime.strftime('%Y-%m-%d %H:%M') if pickup_datetime else None,
        'items': items_response
    }), 201