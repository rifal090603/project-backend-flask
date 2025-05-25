from flask_socketio import join_room
from app.extensions import socketio

@socketio.on('join')
def handle_join(data):
    user_id = str(data.get("user_id"))  
    if user_id:
        join_room(user_id)
        print(f"User {user_id} bergabung ke room {user_id}")
