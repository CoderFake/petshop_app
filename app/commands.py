import click
from app.extensions import db
from app.models import Role, User, Permission
from flask.cli import with_appcontext


def register_commands(app):
    app.cli.add_command(seed_db)
    app.cli.add_command(create_admin)
    app.cli.add_command(init_permissions)


@click.command('seed-db')
@with_appcontext
def seed_db():
    roles = {
        'Admin': Role.get_by_name('Admin') or Role(name='Admin'),
        'User': Role.get_by_name('User') or Role(name='User')
    }

    for role in roles.values():
        if not role.id:
            db.session.add(role)
    db.session.commit()

    categories = [
        'Cats',
        'Dogs',
        'Birds',
        'Fish',
        'Small Pets'
    ]

    from app.models import Category
    for cat_name in categories:
        if not Category.get_by_name(cat_name):
            category = Category(name=cat_name)
            db.session.add(category)

    db.session.commit()
    click.echo('Database seeded successfully!')


@click.command('create-admin')
@click.argument('email')
@click.argument('name')
@click.password_option()
@with_appcontext
def create_admin(email, name, password):
    admin_role = Role.get_by_name('Admin')
    if not admin_role:
        admin_role = Role(name='Admin')
        db.session.add(admin_role)
        db.session.commit()

    existing_user = User.get_by_email(email)
    if existing_user:
        click.echo(f'User with email {email} already exists!')
        return

    admin = User(
        name=name,
        email=email,
        role_id=admin_role.id,
        is_active=True
    )
    admin.password = password

    db.session.add(admin)
    db.session.commit()

    click.echo(f'Admin user {email} created successfully!')


@click.command('init-permissions')
@with_appcontext
def init_permissions():
    permissions = [
        ('user_view', 'Xem danh sách người dùng'),
        ('user_create', 'Tạo người dùng mới'),
        ('user_edit', 'Chỉnh sửa thông tin người dùng'),
        ('user_delete', 'Xóa người dùng'),

        ('product_view', 'Xem danh sách sản phẩm'),
        ('product_create', 'Tạo sản phẩm mới'),
        ('product_edit', 'Chỉnh sửa thông tin sản phẩm'),
        ('product_delete', 'Xóa sản phẩm'),

        ('category_view', 'Xem danh sách danh mục'),
        ('category_create', 'Tạo danh mục mới'),
        ('category_edit', 'Chỉnh sửa thông tin danh mục'),
        ('category_delete', 'Xóa danh mục'),

        ('order_view', 'Xem danh sách đơn hàng'),
        ('order_edit', 'Cập nhật trạng thái đơn hàng'),
        ('order_delete', 'Xóa đơn hàng'),

        ('feedback_view', 'Xem đánh giá và phản hồi'),
        ('feedback_reply', 'Phản hồi đánh giá'),
        ('feedback_delete', 'Xóa đánh giá'),

        ('stats_view', 'Xem thống kê và báo cáo'),
    ]

    for name, description in permissions:
        if not Permission.get_by_name(name):
            permission = Permission(name=name, description=description)
            db.session.add(permission)

    db.session.commit()

    admin_role = Role.get_by_name('Admin')
    if admin_role:
        all_permissions = Permission.query.filter_by(is_deleted=False).all()
        admin_role.permissions = all_permissions
        db.session.commit()

    user_role = Role.get_by_name('User')
    if user_role:
        basic_permissions = Permission.query.filter(
            Permission.name.in_(['product_view', 'category_view', 'feedback_view']),
            Permission.is_deleted == False
        ).all()
        user_role.permissions = basic_permissions
        db.session.commit()

    click.echo('Permissions initialized successfully!')