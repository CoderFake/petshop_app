from app.extensions import db, ma
from app.models.base import BaseModel
from app.utils.validators import validate_email_format
from sqlalchemy.orm import relationship
from marshmallow import fields, validates, ValidationError
from datetime import datetime


class Order(BaseModel):
    __tablename__ = 'orders'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    fullname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(
        db.Enum('pending', 'processing', 'completed', 'cancelled', name='order_status'),
        default='pending',
        nullable=False
    )

    user = relationship('User', back_populates='orders')
    order_details = relationship('OrderDetail', back_populates='order', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.id} - {self.status}>'

    @classmethod
    def get_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id, is_deleted=False).all()

    @classmethod
    def get_by_status(cls, status):
        return cls.query.filter_by(status=status, is_deleted=False).all()

    def cancel(self):
        if self.status != 'completed':
            self.status = 'cancelled'
            return self.save()
        return False

    def update_total_price(self):
        total = sum(detail.price * detail.quantity for detail in self.order_details)
        self.total_price = total
        return self.save()


class OrderSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Order
        load_instance = True

    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    total_price = fields.Decimal(required=True, as_string=True)
    fullname = fields.String(required=True)
    email = fields.Email(required=True)
    order_date = fields.DateTime(dump_only=True)
    status = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    user = fields.Nested('UserSchema', dump_only=True, only=('id', 'name', 'email'))
    order_details = fields.Nested('OrderDetailSchema', dump_only=True, many=True)

    @validates('email')
    def validate_email(self, email):
        if not validate_email_format(email):
            raise ValidationError('Invalid email format')

    @validates('fullname')
    def validate_fullname(self, fullname):
        if not fullname or len(fullname.strip()) == 0:
            raise ValidationError('Full name cannot be empty')

        if len(fullname) > 255:
            raise ValidationError('Full name must be less than 255 characters')

    @validates('total_price')
    def validate_total_price(self, total_price):
        try:
            price_val = float(total_price)
            if price_val < 0:
                raise ValidationError('Total price cannot be negative')
        except (ValueError, TypeError):
            raise ValidationError('Invalid price format')