from app.extensions import db, ma
from app.models.base import BaseModel
from sqlalchemy.orm import relationship
from marshmallow import fields, validates, ValidationError


class OrderDetail(BaseModel):
    __tablename__ = 'order_details'

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    order = relationship('Order', back_populates='order_details')
    product = relationship('Product', back_populates='order_details')

    def __repr__(self):
        return f'<OrderDetail {self.order_id}-{self.product_id}>'

    @property
    def subtotal(self):
        return float(self.price) * self.quantity


class OrderDetailSchema(ma.SQLAlchemySchema):

    class Meta:
        model = OrderDetail
        load_instance = True

    id = fields.Integer(dump_only=True)
    order_id = fields.Integer(required=True)
    product_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True)
    price = fields.Decimal(required=True, as_string=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    subtotal = fields.Method("get_subtotal", dump_only=True)

    product = fields.Nested('ProductSchema', dump_only=True,
                            only=('id', 'title', 'thumbnail'))

    def get_subtotal(self, obj):
        return float(obj.price) * obj.quantity

    @validates('quantity')
    def validate_quantity(self, quantity):
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValidationError('Quantity must be a positive integer')

    @validates('price')
    def validate_price(self, price):
        try:
            price_val = float(price)
            if price_val <= 0:
                raise ValidationError('Price must be greater than zero')
        except (ValueError, TypeError):
            raise ValidationError('Invalid price format')