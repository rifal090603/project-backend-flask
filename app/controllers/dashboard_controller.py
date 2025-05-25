from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from app.models.menu_models import Menu
from app.models.cart_models import CartItem
from app.models.transaction import Transaction
from app.models.auth_models import User
from app.controllers import menu_controller
from datetime import datetime, timedelta
from app.extensions import socketio
from app import db

# Cek apakah user adalah admin
def is_admin():
    user_id = get_jwt_identity()  
    user = User.query.get(user_id)  
    if user and user.role == 'admin': 
        return True
    return False


# Dashboard utama
def dashboard_data():
    if not is_admin():  
        return None, {'message': 'Akses ditolak, Hanya Admin'}, 403

    menu_count = Menu.query.count()
    user_count = User.query.count()
    transaction_count = Transaction.query.count()
    total_income = db.session.query(
        db.func.sum(Transaction.total_amount)
    ).filter(Transaction.status != 'canceled').scalar() or 0

    cart_items = CartItem.query.all()
    cart_data = [{
        'id': item.id,
        'menu': item.menu_id,
        'nama_menu': item.menu.nama,
        'quantity': item.quantity
    } for item in cart_items]

    users = User.query.all()
    admins = [u for u in users if u.role == 'admin']
    clients = [u for u in users if u.role == 'client']

    return {
        'jumlah_menu': menu_count,
        'jumlah_user': user_count,
        'jumlah_transaksi': transaction_count,
        'total_pendapatan': total_income,
        'keranjang_aktif': cart_data,
        'users': users,
        'admins': admins,
        'clients': clients,
        'transaksi': Transaction.query.all(),
        'menus': Menu.query.all()
    }, None, 200


# Ambil data user
def get_user_data():
    if not is_admin():
        return None, None, {'message': 'Akses ditolak'}, 403

    users = User.query.all()
    admins = [user for user in users if user.role == 'admin']
    clients = [user for user in users if user.role == 'client']

    return admins, clients, None, 200

# menampilkan data transaksi
def get_transaksi_data(tanggal_filter=None):
    if not is_admin():
        return jsonify({'message': 'Akses ditolak'}), 403

    try:
        # Parsing tanggal dari filter atau pakai hari ini
        if tanggal_filter:
            tanggal = datetime.strptime(tanggal_filter, '%Y-%m-%d')
        else:
            tanggal = datetime.today()

        # Set range dari awal hari sampai akhir hari
        start_day = datetime(tanggal.year, tanggal.month, tanggal.day)
        end_day = start_day + timedelta(days=1)

        print(f"Filter Tanggal - Start Day: {start_day}, End Day: {end_day}")

        transaksi_list = Transaction.query.filter(
            Transaction.created_at >= start_day,
            Transaction.created_at < end_day
        ).order_by(Transaction.created_at.desc()).all()

        transaksi_data = []

        for transaksi in transaksi_list:
            transaksi_dict = {
                'id': transaksi.id,
                'user_id': transaksi.user_id,
                'client_name': transaksi.client_name,
                'phone_number': transaksi.phone_number,
                'order_type': transaksi.order_type,
                'total_amount': transaksi.total_amount,
                'alamat': transaksi.alamat,
                'no_meja': transaksi.no_meja,
                'status': transaksi.status,
                'is_verified': transaksi.is_verified,
                'payment_method': transaksi.payment_method,
                'pickup_datetime': transaksi.pickup_datetime.strftime('%Y-%m-%d %H:%M:%S') if transaksi.pickup_datetime else None,
                'created_at': transaksi.created_at.strftime('%Y-%m-%d %H:%M:%S') if transaksi.created_at else None,
                'items': []
            }

            for item in transaksi.item:
                menu = Menu.query.get(item.menu_id)
                transaksi_dict['items'].append({
                    'id': item.id,
                    'menu_id': item.menu_id,
                    'nama_menu': menu.nama if menu else "Menu tidak ditemukan",
                    'quantity': item.quantity
                })

            transaksi_data.append(transaksi_dict)

        return jsonify({'transactions': transaksi_data}), 200

    except ValueError:
        return jsonify({'message': 'Format tanggal tidak valid. Gunakan YYYY-MM-DD'}), 400

    except Exception as e:
        return jsonify({
            'message': 'Terjadi kesalahan saat mengambil data transaksi',
            'error': str(e)
        }), 500


# Selesaikan transaksi
def complete_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({'success': False, 'message': 'Transaksi tidak ditemukan'}), 404
    
    transaction.status = 'completed'
    db.session.commit()

    if transaction.user_id:
        user_room = str(transaction.user_id)  
        socketio.emit(
            'transaksi_update',
            {
                'transaction_id': transaction.id,
                'status': 'completed',
                'message': 'Transaksi Anda telah diselesaikan.'
            },
            to=user_room  # pakai string UUID sebagai room
        )

    return jsonify({'success': True, 'message': 'Transaksi selesai'}), 200


# Batalkan transaksi
def cancel_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({'success': False, 'message': 'Transaksi tidak ditemukan'}), 404
    
    if transaction.status != 'pending_payment':
        return jsonify({'success': False, 'message': 'Transaksi tidak dapat dibatalkan'}), 400

    for item in transaction.item:
        menu = item.menu
        if menu:
            menu.stock += item.quantity

    transaction.status = 'canceled'
    db.session.commit()
    
    if transaction.user_id:
        user_room = str(transaction.user_id)
        socketio.emit(
            'transaksi_update',
            {
                'transaction_id': transaction.id,
                'status': 'canceled',
                'message': 'Transaksi Anda telah dibatalkan oleh admin.'
            },
            to=user_room
        )


    return jsonify({'success': True, 'message': 'Transaksi dibatalkan'}), 200
