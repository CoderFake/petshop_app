from app.extensions import db, ma
from app.models.base import BaseModel
from sqlalchemy.orm import relationship
from marshmallow import fields, validates, ValidationError


class ProductGallery(BaseModel):
    __tablename__ = 'product_gallery'

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    thumbnail = db.Column(db.String(255), nullable=True)
    display_order = db.Column(db.Integer, default=0)

    product = relationship('Product', back_populates='gallery')

    def __repr__(self):
        return f'<ProductGallery {self.id} - {self.product_id}>'

    @classmethod
    def get_by_product(cls, product_id):
        return cls.query.filter_by(
            product_id=product_id, is_deleted=False
        ).order_by(cls.display_order).all()


class ProductGallerySchema(ma.SQLAlchemySchema):

    class Meta:
        model = ProductGallery
        load_instance = True

    id = fields.Integer(dump_only=True)
    product_id = fields.Integer(required=True)
    image_url = fields.String(required=True)
    thumbnail = fields.String()
    display_order = fields.Integer()
    created_at = fields.DateTime(dump_only=True)

    @validates('image_url')
    def validate_image_url(self, image_url):
        if not image_url or len(image_url.strip()) == 0:
            raise ValidationError('Image URL cannot be empty')

        if len(image_url) > 255:
            raise ValidationError('Image URL must be less than 255 characters')

    @validates('product_id')
    def validate_product_id(self, product_id):
        from app.models.product import Product
        product = Product.get_by_id(product_id)
        if not product:
            raise ValidationError('Invalid product')