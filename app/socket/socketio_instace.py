# from flask_socketio import SocketIO, emit
# from flask import request

# socketio = SocketIO(cors_allowed_origins="*")
# transaction_sockets = {}

# @socketio.on('register_transaction')
# def register_transaction(data):
#     trx_id = str(data.get('transaction_id'))
#     if trx_id:
#         transaction_sockets[trx_id] = request.sid
#         print(f"Registered {trx_id} to {request.sid}")

# @socketio.on('disconnect')
# def handle_disconnect():
#     sid = request.sid
#     for trx_id, stored_sid in list(transaction_sockets.items()):
#         if stored_sid == sid:
#             del transaction_sockets[trx_id]
#             print(f"Disconnected: {trx_id}")
