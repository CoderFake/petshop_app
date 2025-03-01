from app.extensions import db, ma
from app.models.base import BaseModel
from app.utils.validators import validate_email_format
from sqlalchemy.orm import relationship
from marshmallow import fields, validates, ValidationError


class Feedback(BaseModel):
    __tablename__ = 'feedback'

    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5, nullable=False)

    user = relationship('User', back_populates='feedback')
    product = relationship('Product', back_populates='feedback')

    def __repr__(self):
        return f'<Feedback {self.id} - {self.rating}/5>'

    @classmethod
    def get_by_product(cls, product_id):
        return cls.query.filter_by(
            product_id=product_id, is_deleted=False
        ).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_average_rating(cls, product_id):
        from sqlalchemy import func
        result = db.session.query(func.avg(cls.rating)).filter_by(
            product_id=product_id, is_deleted=False
        ).scalar()
        return float(result) if result else 0


class FeedbackSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Feedback
        load_instance = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    email = fields.Email(required=True)
    user_id = fields.Integer()
    product_id = fields.Integer(required=True)
    comment = fields.String(required=True)
    rating = fields.Integer(required=True)
    created_at = fields.DateTime(dump_only=True)

    user = fields.Nested('UserSchema', dump_only=True, only=('id', 'name'))
    product = fields.Nested('ProductSchema', dump_only=True, only=('id', 'title'))

    @validates('email')
    def validate_email(self, email):
        if not validate_email_format(email):
            raise ValidationError('Invalid email format')

    @validates('rating')
    def validate_rating(self, rating):
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            raise ValidationError('Rating must be between 1 and 5')

    @validates('comment')
    def validate_comment(self, comment):
        if not comment or len(comment.strip()) == 0:
            raise ValidationError('Comment cannot be empty')