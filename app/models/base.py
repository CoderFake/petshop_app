from datetime import datetime
from app.extensions import db
from sqlalchemy import func


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.TIMESTAMP, server_default=func.now())
    updated_at = db.Column(db.TIMESTAMP, server_default=func.now(),
                           onupdate=func.now())
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)

    @classmethod
    def get_by_id(cls, id):
        """Get model by ID, excluding deleted records."""
        return cls.query.filter_by(id=id, is_deleted=False).first()

    @classmethod
    def get_all(cls, include_deleted=False):
        """Get all records, optionally including deleted ones."""
        if include_deleted:
            return cls.query.all()
        return cls.query.filter_by(is_deleted=False).all()

    def soft_delete(self):
        """Mark record as deleted without removing from database."""
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