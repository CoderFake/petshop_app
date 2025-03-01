from app.extensions import db, ma
from app.models.base import BaseModel
from marshmallow import fields, validates, ValidationError
from sqlalchemy.orm import relationship


class Role(BaseModel):
    __tablename__ = 'roles'

    name = db.Column(db.String(50), nullable=False, unique=True)
    users = relationship('User', back_populates='role')

    def __repr__(self):
        return f'<Role {self.name}>'

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name, is_deleted=False).first()


class RoleSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Role
        load_instance = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates('name')
    def validate_name(self, name):
        if not name or len(name.strip()) == 0:
            raise ValidationError('Role name cannot be empty')
        if len(name) > 50:
            raise ValidationError('Role name must be less than 50 characters')