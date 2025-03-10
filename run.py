import os
import sys
from dotenv import load_dotenv
from app.config import config
from app import create_app
from app.extensions import db
from app.models import (
    Role, User, Category, Product,
    Order, OrderDetail, Feedback, ProductGallery
)

load_dotenv()

use_sqlite = '--sql' in sys.argv
use_mysql = '--mysql' in sys.argv

config_name = os.getenv('FLASK_CONFIG') or 'default'
app_config = config[config_name]

if use_sqlite:
    print("Using SQLite database")
    app_config = app_config.use_sqlite()
elif use_mysql:
    print("Using MySQL database")

app = create_app(config_name)

@app.cli.command('init-db')
def init_db():
    db.create_all()

    if not Role.query.first():
        admin_role = Role(name='Admin')
        user_role = Role(name='User')
        db.session.add_all([admin_role, user_role])
        db.session.commit()

        if not User.query.first():
            admin = User(
                name='Administrator',
                email='admin@example.com',
                role_id=admin_role.id
            )
            admin.password = 'Admin@123'
            db.session.add(admin)
            db.session.commit()

    print('Database initialized successfully!')


@app.cli.command('create-sample-data')
def create_sample_data():
    if Product.query.count() > 0:
        print('Sample data already exists. Skipping...')
        return

    categories = [
        Category(name='Chó cưng'),
        Category(name='Mèo cưng'),
        Category(name='Thức ăn'),
        Category(name='Phụ kiện'),
        Category(name='Đồ chơi')
    ]
    db.session.add_all(categories)
    db.session.commit()

    print('Sample data created successfully!')


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Role': Role,
        'User': User,
        'Category': Category,
        'Product': Product,
        'Order': Order,
        'OrderDetail': OrderDetail,
        'Feedback': Feedback,
        'ProductGallery': ProductGallery
    }


if __name__ == '__main__':
    use_sqlite = '--sql' in sys.argv
    use_mysql = '--mysql' in sys.argv

    if use_sqlite and '--sql' in sys.argv:
        sys.argv.remove('--sql')
    if use_mysql and '--mysql' in sys.argv:
        sys.argv.remove('--mysql')

    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))