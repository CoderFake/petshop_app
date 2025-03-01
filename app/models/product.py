from app.extensions import db, ma
from app.models.base import BaseModel
from sqlalchemy.orm import relationship
from marshmallow import fields, validates, ValidationError


class Product(BaseModel):
    __tablename__ = 'products'

    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    thumbnail = db.Column(db.String(255), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    category = relationship('Category', back_populates='products')
    order_details = relationship('OrderDetail', back_populates='product')
    feedback = relationship('Feedback', back_populates='product')
    gallery = relationship('ProductGallery', back_populates='product')

    def __repr__(self):
        return f'<Product {self.title}>'

    @classmethod
    def get_by_category(cls, category_id):
        return cls.query.filter_by(
            category_id=category_id, is_deleted=False
        ).all()

    @classmethod
    def search(cls, keyword=None, category_id=None, min_price=None, max_price=None):
        query = cls.query.filter_by(is_deleted=False)

        if keyword:
            search = f"%{keyword}%"
            query = query.filter(
                db.or_(
                    cls.title.like(search),
                    cls.description.like(search)
                )
            )

        if category_id:
            query = query.filter_by(category_id=category_id)

        if min_price is not None:
            query = query.filter(cls.price >= min_price)

        if max_price is not None:
            query = query.filter(cls.price <= max_price)

        return query.all()


class ProductSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Product
        load_instance = True

    id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    price = fields.Decimal(required=True, as_string=True)
    description = fields.String()
    image = fields.String()
    thumbnail = fields.String()
    category_id = fields.Integer(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Nested relationships
    category = fields.Nested('CategorySchema', dump_only=True, only=('id', 'name'))
    gallery = fields.Nested('ProductGallerySchema', dump_only=True, many=True)

    @validates('title')
    def validate_title(self, title):
        if not title or len(title.strip()) == 0:
            raise ValidationError('Product title cannot be empty')

        if len(title) > 255:
            raise ValidationError('Product title must be less than 255 characters')

    @validates('price')
    def validate_price(self, price):
        try:
            price_val = float(price)
            if price_val <= 0:
                raise ValidationError('Price must be greater than zero')
        except (ValueError, TypeError):
            raise ValidationError('Invalid price format')

    @validates('category_id')
    def validate_category(self, category_id):
        from app.models.category import Category
        category = Category.get_by_id(category_id)
        if not category:
            raise ValidationError('Invalid category')