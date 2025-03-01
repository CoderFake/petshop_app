from app.extensions import db, ma
from app.models.base import BaseModel
from app.utils.validators import validate_email_format
from sqlalchemy.orm import relationship
from marshmallow import fields, validates, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash


class User(BaseModel):
    __tablename__ = 'users'

    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column('password', db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    role = relationship('Role', back_populates='users')
    orders = relationship('Order', back_populates='user')
    feedback = relationship('Feedback', back_populates='user')

    def __repr__(self):
        return f'<User {self.email}>'

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email, is_deleted=False).first()


class UserSchema(ma.SQLAlchemySchema):

    class Meta:
        model = User
        load_instance = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(load_only=True, required=True)
    role_id = fields.Integer(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    role = fields.Nested('RoleSchema', dump_only=True, only=('id', 'name'))

    @validates('email')
    def validate_email(self, email):
        if not validate_email_format(email):
            raise ValidationError('Invalid email format')

        existing_user = User.get_by_email(email)
        if existing_user and (not self.context.get('user_id') or
                              existing_user.id != self.context.get('user_id')):
            raise ValidationError('Email already registered')

    @validates('password')
    def validate_password(self, password):
        if not password or len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long')