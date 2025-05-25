from app import db
from datetime import datetime
import uuid

class TransactionItem(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = db.Column(db.String(36), db.ForeignKey('transaction.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=True)
    product_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    menu = db.relationship("Menu", backref="transaction_items")
    
    def to_dict(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "menu_id": self.menu_id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "price": self.price,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

