from app import db
from datetime import datetime
import uuid

class CartItem(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    menu_id = db.Column(
        db.Integer,
        db.ForeignKey('menu.id', ondelete='CASCADE'),
        nullable=False
    )
    user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id', ondelete='CASCADE'), 
        nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    menu = db.relationship(
        'Menu',
        backref=db.backref('cart_items', lazy=True, cascade='all, delete'),
        passive_deletes=True
    )

    def __repr__(self):
        return f"<CartItem menu_id={self.menu_id} quantity={self.quantity}>"

    def to_dict(self):
        return {
            'id': self.id,
            'menu_id': self.menu_id,
            'nama_menu': self.menu.nama if self.menu else '-',
            'quantity': self.quantity
        }
