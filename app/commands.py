import click
from app.extensions import db
from app.models import Role, User
from flask.cli import with_appcontext


def register_commands(app):
    app.cli.add_command(seed_db)
    app.cli.add_command(create_admin)


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
        role_id=admin_role.id
    )
    admin.password = password

    db.session.add(admin)
    db.session.commit()

    click.echo(f'Admin user {email} created successfully!')