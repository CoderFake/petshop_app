from app.extensions import db, ma
from app.models.base import BaseModel
from marshmallow import fields, validates, ValidationError


class Permission(BaseModel):
    __tablename__ = 'permissions'

    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Permission {self.name}>'

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name, is_deleted=False).first()


class PermissionSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Permission
        load_instance = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    description = fields.String()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates('name')
    def validate_name(self, name):
        if not name or len(name.strip()) == 0:
            raise ValidationError('Tên quyền không được để trống')
        if len(name) > 50:
            raise ValidationError('Tên quyền không được vượt quá 50 ký tự')

        existing = Permission.get_by_name(name)
        if existing and (not self.context.get('permission_id') or
                         existing.id != self.context.get('permission_id')):
            raise ValidationError('Tên quyền này đã tồn tại')