from app.extensions import db, ma
from app.models.base import BaseModel
from sqlalchemy.orm import relationship
from marshmallow import fields, validates, ValidationError


class Category(BaseModel):
    __tablename__ = 'categories'

    name = db.Column(db.String(255), nullable=False, unique=True)

    products = relationship('Product', back_populates='category')

    def __repr__(self):
        return f'<Category {self.name}>'

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name, is_deleted=False).first()


class CategorySchema(ma.SQLAlchemySchema):

    class Meta:
        model = Category
        load_instance = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    product_count = fields.Method("get_product_count")

    def get_product_count(self, obj):
        from app.models.product import Product
        return Product.query.filter_by(
            category_id=obj.id, is_deleted=False
        ).count()

    @validates('name')
    def validate_name(self, name):
        if not name or len(name.strip()) == 0:
            raise ValidationError('Category name cannot be empty')

        if len(name) > 255:
            raise ValidationError('Category name must be less than 255 characters')

        existing = Category.get_by_name(name)
        if existing and (not self.context.get('category_id') or
                         existing.id != self.context.get('category_id')):
            raise ValidationError('Category name already exists')