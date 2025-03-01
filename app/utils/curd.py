from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from app.utils.validators import handle_transaction


class CRUDService:
    def __init__(self, model_class):
        self.model_class = model_class

    def get_all(self, include_deleted=False):
        query = self.model_class.query
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
        return query.all()

    def get_by_id(self, id, include_deleted=False):
        query = self.model_class.query.filter_by(id=id)
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
        return query.first()

    def filter_by(self, include_deleted=False, **kwargs):
        query = self.model_class.query.filter_by(**kwargs)
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
        return query.all()

    @handle_transaction
    def create(self, **kwargs):
        instance = self.model_class(**kwargs)
        db.session.add(instance)
        return instance

    @handle_transaction
    def update(self, id, **kwargs):
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            return instance
        return None

    @handle_transaction
    def delete(self, id, soft=True):
        instance = self.get_by_id(id, include_deleted=True)
        if not instance:
            return False

        if soft:
            instance.is_deleted = True
            return True
        else:
            db.session.delete(instance)
            return True

    @handle_transaction
    def restore(self, id):

        instance = self.model_class.query.filter_by(id=id, is_deleted=True).first()
        if instance:
            instance.is_deleted = False
            return instance
        return None