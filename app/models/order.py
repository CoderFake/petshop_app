from app.extensions import db, ma
from app.models.base import BaseModel
from app.utils.validators import validate_email_format
from app.utils.datetime_helpers import get_current_time, utc_to_local, format_datetime
from sqlalchemy.orm import relationship
from marshmallow import fields, validates, ValidationError
from datetime import datetime


class Order(BaseModel):
    __tablename__ = 'orders'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    fullname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(
        db.Enum('pending', 'processing', 'shipped', 'delivered', 'cancelled', name='order_status'),
        default='pending',
        nullable=False
    )
    payment_method = db.Column(
        db.Enum('cod', 'vnpay', name='payment_method'),
        default='cod',
        nullable=False
    )
    payment_status = db.Column(
        db.Enum('pending', 'paid', 'refunded', 'failed', name='payment_status'),
        default='pending',
        nullable=False
    )
    transaction_id = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)

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
        if self.status not in ['shipped', 'delivered']:
            self.status = 'cancelled'
            return self.save()
        return False

    def update_total_price(self):
        total = sum(detail.price * detail.quantity for detail in self.order_details)
        self.total_price = total
        return self.save()

    def mark_as_paid(self, transaction_id=None):
        self.payment_status = 'paid'
        if transaction_id:
            self.transaction_id = transaction_id
        return self.save()

    def request_refund(self):
        if self.payment_status == 'paid':
            self.payment_status = 'refunded'
            return self.save()
        return False

    def get_local_order_date(self):
        if self.order_date:
            return utc_to_local(self.order_date)
        return None

    def get_formatted_order_date(self, format='%d/%m/%Y %H:%M'):
        return format_datetime(self.order_date, format)


class OrderSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Order
        load_instance = True

    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    total_price = fields.Decimal(required=True, as_string=True)
    fullname = fields.String(required=True)
    email = fields.Email(required=True)
    phone = fields.String(required=True)
    address = fields.String(required=True)
    order_date = fields.DateTime(dump_only=True)
    status = fields.String(dump_only=True)
    payment_method = fields.String(required=True)
    payment_status = fields.String(dump_only=True)
    transaction_id = fields.String(dump_only=True)
    notes = fields.String()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    formatted_order_date = fields.Method("get_formatted_order_date")

    user = fields.Nested('UserSchema', dump_only=True, only=('id', 'name', 'email'))
    order_details = fields.Nested('OrderDetailSchema', dump_only=True, many=True)

    def get_formatted_order_date(self, obj):
        """Format order date for display."""
        return obj.get_formatted_order_date()

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

    @validates('phone')
    def validate_phone(self, phone):
        if not phone or len(phone.strip()) == 0:
            raise ValidationError('Phone number cannot be empty')

        if not phone.isdigit():
            raise ValidationError('Phone number must contain only digits')

    @validates('total_price')
    def validate_total_price(self, total_price):
        try:
            price_val = float(total_price)
            if price_val < 0:
                raise ValidationError('Total price cannot be negative')
        except (ValueError, TypeError):
            raise ValidationError('Invalid price format')

    @validates('payment_method')
    def validate_payment_method(self, payment_method):
        if payment_method not in ['cod', 'vnpay']:
            raise ValidationError('Invalid payment method')