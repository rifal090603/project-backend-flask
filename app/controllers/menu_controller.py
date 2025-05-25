from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.models.menu_models import Menu
from app import db
import traceback
import os

# Memeriksa apakah ekstensi file diperbolehkan
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
           
           
# Mendapatkan semua menu
def get_all_menu():
    try:
        # Ambil parameter dari query string
        page = request.args.get('page', default=1, type=int)
        per_page = 15
        category = request.args.get('category', default=None, type=str)

        # Filter berdasarkan kategori jika diberikan
        query = Menu.query
        if category and category != "All":
            query = query.filter(Menu.category == category)

        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        menus = pagination.items

        # Membuat list dict menu
        result = []
        for menu in menus:
            result.append({
                "id": menu.id,
                "nama": menu.nama,
                "harga": menu.harga,
                "stock": menu.stock,
                "category": menu.category,
                "image": menu.image,
                "deskripsi": menu.deskripsi
            })

        # Struktur response pagination
        response = {
            "menus": result,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_pages": pagination.pages,
            "total_items": pagination.total,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Mendapatkan menu berdasarkan id
def get_menu_by_id(menu_id):
    menu = Menu.query.get(menu_id)
    if menu:
        return jsonify({
            "id": menu.id,
            "nama": menu.nama,
            "harga": menu.harga,
            "stock": menu.stock,
            "category": menu.category,
            "image": menu.image,
            "deskripsi":menu.deskripsi,
            "created_at": menu.create_at.strftime('%Y-%m-%d %H:%M:%S')
        }), 200
    return jsonify({'message': 'Manu not found'}), 404

# Menambah menu baru
def create_menu():
    nama = request.form.get('nama')
    harga = request.form.get('harga')
    stock = request.form.get('stock')
    category = request.form.get('category')
    deskripsi = request.form.get('deskripsi')
    image_file = request.files.get('image')

    print(f"Received data: nama={nama}, harga={harga}, stock={stock}, category={category}, deskripsi={deskripsi}")

    if not nama or not harga or not stock or not category:
        print("Validation failed: Some fields are empty")
        return jsonify({"message": "Field tidak boleh kosong"}), 400

    try:
        harga = float(harga)
        stock = int(stock)
    except ValueError:
        print(f"Error in converting harga: {harga} or stock: {stock}")
        return jsonify({"message": "Harga dan stok harus berupa angka"}), 400

    filename = None
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        image_path = os.path.join(upload_folder, filename)
        image_file.save(image_path)

    # Menambahkan menu baru ke database
    try:
        new_menu = Menu(
            nama=nama,
            harga=harga,
            stock=stock,
            category=category,
            image=filename,
            deskripsi=deskripsi
        )
        db.session.add(new_menu)
        db.session.commit()

        print("Menu successfully created")

        # Mengembalikan respons setelah berhasil menambah menu
        return jsonify({
            "message": "Menu berhasil ditambahkan",
            "data": {
                "id": new_menu.id,
                "nama": new_menu.nama,
                "harga": new_menu.harga,
                "stock": new_menu.stock,
                "category": new_menu.category,
                "deskripsi": new_menu.deskripsi,
                "image": new_menu.image
            }
        }), 201
    except Exception as e:
        print(f"Error occurred during menu creation: {str(e)}")
        return jsonify({"message": "Error creating menu"}), 500
    
    
# Update manu
def update_menu(menu_id):
    menu = Menu.query.get(menu_id)
    if not menu:
        return jsonify({'message': 'Menu tidak ditemukan'}), 404

    # Ambil data dari JSON body
    data = request.form

    nama = data.get('nama', menu.nama)
    harga = data.get('harga', menu.harga)
    stock = data.get('stock', menu.stock)
    category = data.get('category', menu.category)
    deskripsi = data.get('deskripsi', menu.deskripsi)
    
    
    try:
        harga = float(harga)
    except (TypeError, ValueError):
        return jsonify({"message": "Harga harus berupa angka"}), 400
    
    file = request.files.get('image')
    if file:
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']  # ambil dari config
        save_path = os.path.join(upload_folder, filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        file.save(save_path)
        menu.image = filename
        
    # Update data
    menu.nama = nama
    menu.harga = harga
    menu.stock = stock
    menu.category = category
    menu.deskripsi = deskripsi
    
    
    db.session.commit()
    
    return jsonify({
         'message': 'Menu berhasil diperbarui',
        'data': {
            'id': menu.id,
            'name': menu.nama,
            'harga': menu.harga,
            'stock': menu.stock,
            'category': menu.category,
            'image': menu.image,
            "deskripsi": menu.deskripsi,
            'created_at': menu.create_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    }), 200



def delete_menu(menu_id):
    menu = Menu.query.get(menu_id)
    if not menu:
        return jsonify({'message': 'Menu not found'}), 404

    try:
        db.session.delete(menu)
        db.session.commit()
        return jsonify({'message': 'Menu deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print("Error occurred while deleting menu:", e)
        traceback.print_exc()  # Ini akan menampilkan stack trace ke console/log
        return jsonify({'message': 'Failed to delete menu', 'error': str(e)}), 500

