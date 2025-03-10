from datetime import datetime
from app.extensions import db
from sqlalchemy import func
from app.utils.datetime_helpers import get_current_time, utc_to_local


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.TIMESTAMP, server_default=func.now())
    updated_at = db.Column(db.TIMESTAMP, server_default=func.now(),
                           onupdate=func.now())
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id, is_deleted=False).first()

    @classmethod
    def get_all(cls, include_deleted=False):
        if include_deleted:
            return cls.query.all()
        return cls.query.filter_by(is_deleted=False).all()

    def soft_delete(self):
        self.is_deleted = True
        db.session.commit()

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error saving {self.__class__.__name__}: {str(e)}")
            return False

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self.save()

    def get_local_created_at(self):
        if self.created_at:
            return utc_to_local(self.created_at)
        return None

    def get_local_updated_at(self):
        if self.updated_at:
            return utc_to_local(self.updated_at)
        return None