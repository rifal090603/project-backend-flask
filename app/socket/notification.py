# # app/socket/notification.py
# from app.extensions import socketio
# from app.models.transaction import Transaction
# from app import db

# def send_status_notification(user_id, status):
#     room = f"user_{user_id}"
#     message = f"Status transaksi Anda telah diperbarui menjadi: {status}"

#     print(f"[SocketIO] Kirim notifikasi ke {room}: {message}")

#     socketio.emit('new_notification', {
#         'message': message,
#         'status': status
#     }, room=room)

