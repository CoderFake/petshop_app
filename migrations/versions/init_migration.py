from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = 'e8f01a2c57d1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Tạo bảng roles
    op.create_table('roles',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=50), nullable=False),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('updated_at', sa.TIMESTAMP(),
                              server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('0')),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
                    )

    # Tạo bảng permissions
    op.create_table('permissions',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=50), nullable=False),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('updated_at', sa.TIMESTAMP(),
                              server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('0')),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
                    )

    # Tạo bảng role_permissions
    op.create_table('role_permissions',
                    sa.Column('role_id', sa.Integer(), nullable=False),
                    sa.Column('permission_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
                    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
                    sa.PrimaryKeyConstraint('role_id', 'permission_id')
                    )

    # Tạo bảng users
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.Column('email', sa.String(length=255), nullable=False),
                    sa.Column('password', sa.String(length=255), nullable=False),
                    sa.Column('role_id', sa.Integer(), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('0')),
                    sa.Column('verification_token', sa.String(length=255), nullable=True),
                    sa.Column('token_expiry', sa.DateTime(), nullable=True),
                    sa.Column('phone', sa.String(length=20), nullable=True),
                    sa.Column('address', sa.String(length=255), nullable=True),
                    sa.Column('avatar', sa.String(length=255), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('updated_at', sa.TIMESTAMP(),
                              server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('0')),
                    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email')
                    )

    # Tạo bảng categories
    op.create_table('categories',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('updated_at', sa.TIMESTAMP(),
                              server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('0')),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
                    )

    # Tạo bảng products
    op.create_table('products',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.String(length=255), nullable=False),
                    sa.Column('price', sa.Numeric(10, 2), nullable=False),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('image', sa.String(length=255), nullable=True),
                    sa.Column('thumbnail', sa.String(length=255), nullable=True),
                    sa.Column('category_id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('updated_at', sa.TIMESTAMP(),
                              server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('0')),
                    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    # Tạo bảng orders
    op.create_table('orders',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.Column('total_price', sa.Numeric(10, 2), nullable=False),
                    sa.Column('fullname', sa.String(length=255), nullable=False),
                    sa.Column('email', sa.String(length=255), nullable=False),
                    sa.Column('phone', sa.String(length=20), nullable=False, server_default=sa.text("''")),
                    sa.Column('address', sa.String(length=255), nullable=False, server_default=sa.text("''")),
                    sa.Column('order_date', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
                    sa.Column('status', sa.Enum('pending', 'processing', 'shipped', 'delivered', 'cancelled',
                                                name='order_status'), nullable=False,
                              server_default=sa.text("'pending'")),
                    sa.Column('payment_method', sa.Enum('cod', 'vnpay', name='payment_method'), nullable=False,
                              server_default=sa.text("'cod'")),
                    sa.Column('payment_status', sa.Enum('pending', 'paid', 'refunded', 'failed', name='payment_status'),
                              nullable=False, server_default=sa.text("'pending'")),
                    sa.Column('transaction_id', sa.String(length=255), nullable=True),
                    sa.Column('notes', sa.Text(), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('updated_at', sa.TIMESTAMP(),
                              server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('0')),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    # Tạo bảng order_details
    op.create_table('order_details',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('order_id', sa.Integer(), nullable=False),
                    sa.Column('product_id', sa.Integer(), nullable=False),
                    sa.Column('quantity', sa.Integer(), nullable=False, server_default=sa.text('1')),
                    sa.Column('price', sa.Numeric(10, 2), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('updated_at', sa.TIMESTAMP(),
                              server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('0')),
                    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
                    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    # Tạo bảng feedback
    op.create_table('feedback',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.Column('email', sa.String(length=255), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.Column('product_id', sa.Integer(), nullable=False),
                    sa.Column('comment', sa.Text(), nullable=False),
                    sa.Column('rating', sa.Integer(), nullable=False, server_default=sa.text('5')),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('updated_at', sa.TIMESTAMP(),
                              server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('0')),
                    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    # Tạo bảng product_gallery
    op.create_table('product_gallery',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('product_id', sa.Integer(), nullable=False),
                    sa.Column('image_url', sa.String(length=255), nullable=False),
                    sa.Column('thumbnail', sa.String(length=255), nullable=True),
                    sa.Column('display_order', sa.Integer(), nullable=True, server_default=sa.text('0')),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('updated_at', sa.TIMESTAMP(),
                              server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('0')),
                    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    # Xóa bảng theo thứ tự ngược lại
    op.drop_table('product_gallery')
    op.drop_table('feedback')
    op.drop_table('order_details')
    op.drop_table('orders')
    op.drop_table('products')
    op.drop_table('categories')
    op.drop_table('users')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('roles')