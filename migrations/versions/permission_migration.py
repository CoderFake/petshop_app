from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = 'e8f01a2c57d1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create permissions table
    op.create_table('permissions',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=50), nullable=False),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('updated_at', sa.TIMESTAMP(),
                              server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
                    sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
                    )

    # Create role_permissions association table
    op.create_table('role_permissions',
                    sa.Column('role_id', sa.Integer(), nullable=False),
                    sa.Column('permission_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
                    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
                    sa.PrimaryKeyConstraint('role_id', 'permission_id')
                    )

    # Add description column to roles table
    op.add_column('roles', sa.Column('description', sa.String(length=255), nullable=True))

    # Add new fields to user table
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('0')))
    op.add_column('users', sa.Column('verification_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('token_expiry', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('address', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('avatar', sa.String(length=255), nullable=True))

    # Add new fields to orders table
    op.add_column('orders', sa.Column('phone', sa.String(length=20), nullable=False, server_default=sa.text("''")))
    op.add_column('orders', sa.Column('address', sa.String(length=255), nullable=False, server_default=sa.text("''")))
    op.add_column('orders', sa.Column('payment_method', sa.Enum('cod', 'vnpay', name='payment_method'), nullable=False,
                                      server_default=sa.text("'cod'")))
    op.add_column('orders',
                  sa.Column('payment_status', sa.Enum('pending', 'paid', 'refunded', 'failed', name='payment_status'),
                            nullable=False, server_default=sa.text("'pending'")))
    op.add_column('orders', sa.Column('transaction_id', sa.String(length=255), nullable=True))
    op.add_column('orders', sa.Column('notes', sa.Text(), nullable=True))

    # Make user_id nullable in orders for guest checkout
    op.alter_column('orders', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=True)


def downgrade():
    # Drop columns from orders table
    op.alter_column('orders', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=False)
    op.drop_column('orders', 'notes')
    op.drop_column('orders', 'transaction_id')
    op.drop_column('orders', 'payment_status')
    op.drop_column('orders', 'payment_method')
    op.drop_column('orders', 'address')
    op.drop_column('orders', 'phone')

    # Drop columns from users table
    op.drop_column('users', 'avatar')
    op.drop_column('users', 'address')
    op.drop_column('users', 'phone')
    op.drop_column('users', 'token_expiry')
    op.drop_column('users', 'verification_token')
    op.drop_column('users', 'is_active')

    # Drop description from roles
    op.drop_column('roles', 'description')

    # Drop role_permissions table
    op.drop_table('role_permissions')

    # Drop permissions table
    op.drop_table('permissions')