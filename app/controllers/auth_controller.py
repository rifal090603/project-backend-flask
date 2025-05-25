import uuid
from flask import request, jsonify
from flask_jwt_extended import create_access_token
from app.models.auth_models import User
from app import db

def register_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Data tidak lengkap'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username sudah terdaftar'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email sudah digunakan'}), 409

    new_user = User(
        id=str(uuid.uuid4()),
        username=username,
        email=email
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=str(new_user.id))

    return jsonify({
        'message': 'Registrasi berhasil',
        'token': access_token,
        'user': {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email,
            'role': new_user.role
        }
    }), 201

def register_admin():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Data tidak lengkap'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username sudah digunakan'}), 409

    admin = User(
        id=str(uuid.uuid4()),
        username=username,
        email=email,
        role='admin'
    )
    admin.set_password(password)

    db.session.add(admin)
    db.session.commit()

    access_token = create_access_token(identity=str(admin.id))

    return jsonify({
        'message': 'Admin berhasil dibuat',
        'token': access_token,
        'admin': {
            'id': admin.id,
            'username': admin.username,
            'email': admin.email,
            'role': admin.role
        }
    }), 201

def login_user_controller():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username dan password harus diisi'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = user.generate_jwt() 
        return jsonify({
            'message': 'Login berhasil',
            'token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200

    return jsonify({'message': 'Username atau password salah'}), 401
