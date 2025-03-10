from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_session import Session

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
se = Session()