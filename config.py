import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Memuat file .env
load_dotenv()

# Menentukan direktori dasar
basedir = os.path.abspath(os.path.dirname(__file__))

def get_database_uri():
    mysql_uri = (
        f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}"
    )
    postgres_uri = (
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    )
    sqlite_uri = f"sqlite:///{os.path.join(basedir, 'app.db')}"  # Simpan ke file

    for uri in [mysql_uri, postgres_uri]:
        try:
            engine = create_engine(uri)
            with engine.connect():
                print(f"✅ Connected to: {uri}")
                return uri
        except OperationalError:
            print(f"⚠️ Could not connect to: {uri}")
            continue

    print("❌ All database connections failed. Using SQLite file.")
    return sqlite_uri


class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY')  
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERY = True

    # Konfigurasi upload folder
    UPLOAD_FOLDER = os.path.join(basedir, os.getenv("UPLOAD_FOLDER", "upload"))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    FCM_SERVER_KEY = os.getenv('FCM_SERVER_KEY')

    # Gunakan fungsi luar, bukan staticmethod
    SQLALCHEMY_DATABASE_URI = get_database_uri()
