from app import db
from datetime import datetime
import uuid

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(255), nullable=False)
    harga = db.Column(db.Float, nullable=False)
    stock = db.Column(db.BigInteger, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    deskripsi = db.Column(db.Text, nullable=True)
    create_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
   
    def __init__(self, nama, harga, stock, category, image=None, deskripsi=None):
        self.nama = nama
        self.harga = harga
        self.stock = stock
        self.category = category  
        self.image = image
        self.deskripsi = deskripsi
        
    def to_dict(self):
        return {
            'id': self.id,
            'nama': self.nama,
            'harga': self.harga,
            'stock': self.stock,
            'category': self.category,
            'image': self.image,
            'deskripsi': self.deskripsi,
            'create_at': self.create_at.isoformat() if self.create_at else None
        }
    
    def __repr__(self):
        return "<Menu {}>".format(self.nama)
    
    