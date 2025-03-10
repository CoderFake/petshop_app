import os
from dotenv import load_dotenv
import pytz

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dfkbsvbskasbfda')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SESSION_TYPE = 'filesystem'


    TIMEZONE = os.environ.get('TIMEZONE', 'Asia/Ho_Chi_Minh')
    try:
        pytz.timezone(TIMEZONE)
    except pytz.exceptions.UnknownTimeZoneError:
        TIMEZONE = 'Asia/Ho_Chi_Minh'


class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    SQLALCHEMY_ECHO = True

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL',
        'mysql+pymysql://root:@localhost/petshop_dev?charset=utf8mb4'
    )

    SQLITE_DATABASE_URI = os.environ.get(
        'SQLITE_DATABASE_URL',
        'sqlite:///petshop_dev.sqlite'
    )

    @classmethod
    def use_sqlite(cls):
        cls.SQLALCHEMY_DATABASE_URI = cls.SQLITE_DATABASE_URI
        return cls


class TestingConfig(Config):
    FLASK_ENV = 'testing'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL',
        'mysql+pymysql://root:@localhost/petshop_test?charset=utf8mb4'
    )

    SQLITE_DATABASE_URI = os.environ.get(
        'SQLITE_TEST_DATABASE_URL',
        'sqlite:///petshop_test.sqlite'
    )

    @classmethod
    def use_sqlite(cls):
        cls.SQLALCHEMY_DATABASE_URI = cls.SQLITE_DATABASE_URI
        return cls


class ProductionConfig(Config):
    FLASK_ENV = 'production'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost/petshop?charset=utf8mb4'
    )

    SQLITE_DATABASE_URI = os.environ.get(
        'SQLITE_DATABASE_URL',
        'sqlite:///petshop.sqlite'
    )

    @classmethod
    def use_sqlite(cls):
        cls.SQLALCHEMY_DATABASE_URI = cls.SQLITE_DATABASE_URI
        return cls


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}