from app.extensions import db, ma
from app.models.base import BaseModel
from app.utils.validators import validate_email_format
from sqlalchemy.orm import relationship
from marshmallow import fields, validates, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets


class User(BaseModel):
    __tablename__ = 'users'

    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column('password', db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    verification_token = db.Column(db.String(255), nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    avatar = db.Column(db.String(255), nullable=True)

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

    def generate_verification_token(self, expiry_hours=24):
        self.verification_token = secrets.token_urlsafe(32)
        self.token_expiry = datetime.utcnow() + timedelta(hours=expiry_hours)
        return self.verification_token

    def verify_account(self, token):
        if self.verification_token == token and self.token_expiry > datetime.utcnow():
            self.is_active = True
            self.verification_token = None
            self.token_expiry = None
            return True
        return False

    def has_permission(self, permission):
        if not self.role:
            return False
        return self.role.name == 'Admin' or permission in [p.name for p in self.role.permissions]

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email, is_deleted=False).first()

    @classmethod
    def get_by_token(cls, token):
        return cls.query.filter_by(verification_token=token, is_deleted=False).first()


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(load_only=True, required=True)
    role_id = fields.Integer(required=True)
    is_active = fields.Boolean(dump_only=True)
    phone = fields.String()
    address = fields.String()
    avatar = fields.String()
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

    @validates('phone')
    def validate_phone(self, phone):
        if phone and not phone.isdigit():
            raise ValidationError('Phone number must contain only digits')