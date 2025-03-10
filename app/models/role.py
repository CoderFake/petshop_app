from app.extensions import db, ma
from app.models.base import BaseModel
from marshmallow import fields, validates, ValidationError
from sqlalchemy.orm import relationship

role_permissions = db.Table(
    'role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)


class Permission(BaseModel):
    __tablename__ = 'permissions'

    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Permission {self.name}>'

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name, is_deleted=False).first()


class Role(BaseModel):
    __tablename__ = 'roles'

    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    users = relationship('User', back_populates='role')
    permissions = relationship('Permission', secondary=role_permissions, lazy='subquery')

    def __repr__(self):
        return f'<Role {self.name}>'

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name, is_deleted=False).first()

    def add_permission(self, permission):
        if permission not in self.permissions:
            self.permissions.append(permission)

    def remove_permission(self, permission):
        if permission in self.permissions:
            self.permissions.remove(permission)


class PermissionSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Permission
        load_instance = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    description = fields.String()
    created_at = fields.DateTime(dump_only=True)

    @validates('name')
    def validate_name(self, name):
        if not name or len(name.strip()) == 0:
            raise ValidationError('Permission name cannot be empty')
        if len(name) > 50:
            raise ValidationError('Permission name must be less than 50 characters')


class RoleSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Role
        load_instance = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    description = fields.String()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    permissions = fields.Nested('PermissionSchema', many=True, only=('id', 'name'))

    @validates('name')
    def validate_name(self, name):
        if not name or len(name.strip()) == 0:
            raise ValidationError('Role name cannot be empty')
        if len(name) > 50:
            raise ValidationError('Role name must be less than 50 characters')