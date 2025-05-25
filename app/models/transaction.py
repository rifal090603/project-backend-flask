from app import db
from datetime import datetime
import uuid

class Transaction(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    client_name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(25), nullable=True)
    order_type = db.Column(db.String(50), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    alamat = db.Column(db.Text, nullable=True)
    no_meja = db.Column(db.String(50), nullable=True)
    pickup_datetime = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='pending_payment')
    payment_method = db.Column(db.String(50), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    item = db.relationship("TransactionItem", backref="transaction", cascade="all, delete-orphan")
    user = db.relationship("User", backref=db.backref("transactions", lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'client_name': self.client_name,
            'phone_number': self.phone_number,
            'order_type': self.order_type,
            'alamat': self.alamat,
            'no_meja': self.no_meja,
            'total_amount': self.total_amount,
            'pickup_datetime': self.pickup_datetime.isoformat() if self.pickup_datetime else None,
            'payment_method': self.payment_method,
            'status': self.status,
            'items': [item.to_dict() for item in self.item],
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def is_dine_in(self):
        return self.order_type == 'dine-in'

    def is_delivery(self):
        return self.order_type == 'delivery'

    def is_takeaway(self):
        return self.order_type == 'takeaway'
