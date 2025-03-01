from sqlalchemy.exc import IntegrityError, DataError
from email_validator import validate_email, EmailNotValidError
from app.extensions import db


def validate_and_save(model_instance, raise_exception=False):
    try:
        db.session.add(model_instance)
        db.session.commit()
        return True
    except (IntegrityError, DataError) as e:
        db.session.rollback()
        if raise_exception:
            raise e
        return False


def validate_email_format(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def handle_transaction(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            raise e

    return wrapper