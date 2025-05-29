import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Memuat file .env
load_dotenv()

# Menentukan direktori dasar
basedir = os.path.abspath(os.path.dirname(__file__))

def get_mysql_uri():
    return (
        f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}"
    )

class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERY = True

    UPLOAD_FOLDER = os.path.join(basedir, os.getenv("UPLOAD_FOLDER", "upload"))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB


    # Koneksi hanya ke MySQL
    SQLALCHEMY_DATABASE_URI = get_mysql_uri()
