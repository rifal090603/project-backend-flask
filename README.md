# Coffee Macth - Backend

Ini adalah backend untuk aplikasi **Coffee Macth**, dibangun dengan Flask dan menggunakan TensorFlow + Keras untuk sistem rekomendasi menu berbasis deskripsi produk.

## Fitur

- Autentikasi menggunakan JWT
- API daftar menu & detail menu
- Sistem rekomendasi berdasarkan kemiripan deskripsi produk
- Integrasi model TensorFlow langsung di backend Flask

## Cara Menjalankan

1. Clone repositori:

   ```bash
   git clone https://github.com/rifal090603/project-backend-flask.git
   cd project-backend-flask
   ```

2. Buat dan aktifkan virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate     # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Jalankan backend dengan salah satu cara:
   ```bash
   flask run
   ```

> Secara default akan berjalan di `http://localhost:5000`

## File .env

```bash
FLASK_APP = run.py
FLASK_ENV = development
SECRET_KEY = lighter@123

# MySQL Configuration
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=coba_3
DB_USERNAME=root
DB_PASSWORD=12345

TELEGRAM_BOT_TOKEN=7680731850:AAGABdH_thqfencqR4vGFphBf3-XjWSbpYI
TELEGRAM_CHAT_ID=7921374299


UPLOAD_FOLDER = app/static/upload
```
## Create Admin
- flask create-admin
- ikuti saja intruksi yang diberikan


## Sistem Rekomendasi

- Menggunakan embedding TensorFlow Keras
- Menganalisis deskripsi produk dan mencari menu yang serupa
- Dapat diakses setelah login via halaman detail menu

## Teknologi yang Digunakan

- Flask
- TensorFlow / Keras
- SQLAlchemy
- JWT

## Import Data Menu dari CSV

import data csv ke database:

1. Buat database mysql dengan mengikuti file .env.
2. Jalankan script berikut di Python untuk memasukkan data ke database:

```bash
python import_data.py
```
