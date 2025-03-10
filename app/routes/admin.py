from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app, jsonify
from app.extensions import db
from app.models import User, Role, Permission, Product, Category, Order
from app.utils.decorators import admin_required, permission_required
from app.utils.email import send_email
import json
from datetime import datetime

admin = Blueprint('admin', __name__)


@admin.route('/')
@admin_required
def index():
    users_count = User.query.filter_by(is_deleted=False).count()
    orders_count = Order.query.filter_by(is_deleted=False).count()
    products_count = Product.query.filter_by(is_deleted=False).count()

    recent_orders = Order.query.filter_by(is_deleted=False).order_by(Order.created_at.desc()).limit(5).all()

    pending_orders = Order.query.filter_by(status='pending', is_deleted=False).count()

    return render_template('admin/index.html',
                           users_count=users_count,
                           orders_count=orders_count,
                           products_count=products_count,
                           recent_orders=recent_orders,
                           pending_orders=pending_orders)


@admin.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    users = User.query.filter_by(is_deleted=False).paginate(page=page, per_page=per_page)

    return render_template('admin/users.html', users=users)


@admin.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    user = User.get_by_id(user_id)
    if not user:
        flash('Không tìm thấy người dùng.', 'danger')
        return redirect(url_for('admin.users'))

    return render_template('admin/user_detail.html', user=user)


@admin.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.get_by_id(user_id)
    if not user:
        flash('Không tìm thấy người dùng.', 'danger')
        return redirect(url_for('admin.users'))

    user.is_active = not user.is_active
    if user.save():
        action = "kích hoạt" if user.is_active else "vô hiệu hóa"
        flash(f'Đã {action} tài khoản của {user.name}.', 'success')
    else:
        flash('Có lỗi xảy ra. Vui lòng thử lại.', 'danger')

    return redirect(url_for('admin.user_detail', user_id=user.id))


@admin.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.get_by_id(user_id)
    if not user:
        flash('Không tìm thấy người dùng.', 'danger')
        return redirect(url_for('admin.users'))

    if user.id == session.get('user_id'):
        flash('Không thể xóa tài khoản của chính bạn.', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user.id))

    user.is_deleted = True
    if user.save():
        flash(f'Đã xóa tài khoản của {user.name}.', 'success')
        return redirect(url_for('admin.users'))
    else:
        flash('Có lỗi xảy ra. Vui lòng thử lại.', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user.id))


@admin.route('/products')
@admin_required
def products():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    products = Product.query.filter_by(is_deleted=False).paginate(page=page, per_page=per_page)

    return render_template('admin/products.html', products=products)


@admin.route('/orders')
@admin_required
def orders():
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Order.query.filter_by(is_deleted=False)
    if status:
        query = query.filter_by(status=status)

    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page)

    return render_template('admin/orders.html', orders=orders, current_status=status)


@admin.route('/orders/<int:order_id>')
@admin_required
def order_detail(order_id):
    order = Order.get_by_id(order_id)
    if not order:
        flash('Không tìm thấy đơn hàng.', 'danger')
        return redirect(url_for('admin.orders'))

    return render_template('admin/order_detail.html', order=order)


@admin.route('/orders/<int:order_id>/update-status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    order = Order.get_by_id(order_id)
    if not order:
        flash('Không tìm thấy đơn hàng.', 'danger')
        return redirect(url_for('admin.orders'))

    status = request.form.get('status')
    if status not in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        flash('Trạng thái không hợp lệ.', 'danger')
        return redirect(url_for('admin.order_detail', order_id=order.id))

    order.status = status

    if status == 'delivered' and order.payment_method == 'cod' and order.payment_status == 'pending':
        order.payment_status = 'paid'

    if order.save():
        flash('Cập nhật trạng thái đơn hàng thành công.', 'success')

        try:
            user = User.get_by_id(order.user_id) if order.user_id else None
            if user:
                subject = f"Cập nhật trạng thái đơn hàng #{order.id}"
                template = "order_status_update"
                send_email(order.email, subject, template, user=user, order=order)
        except Exception as e:
            current_app.logger.error(f"Failed to send order update email: {str(e)}")
    else:
        flash('Có lỗi xảy ra. Vui lòng thử lại.', 'danger')

    return redirect(url_for('admin.order_detail', order_id=order.id))


@admin.route('/categories')
@admin_required
def categories():
    """Manage categories"""
    categories = Category.query.filter_by(is_deleted=False).all()
    return render_template('admin/categories.html', categories=categories)


@admin.route('/categories/add', methods=['GET', 'POST'])
@admin_required
def add_category():
    if request.method == 'POST':
        name = request.form.get('name')

        if not name:
            flash('Tên danh mục không được để trống.', 'danger')
            return render_template('admin/add_category.html')

        if Category.get_by_name(name):
            flash('Danh mục này đã tồn tại.', 'danger')
            return render_template('admin/add_category.html')

        category = Category(name=name)
        if category.save():
            flash('Thêm danh mục thành công.', 'success')
            return redirect(url_for('admin.categories'))
        else:
            flash('Có lỗi xảy ra. Vui lòng thử lại.', 'danger')

    return render_template('admin/add_category.html')


@admin.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_category(category_id):

    category = Category.get_by_id(category_id)
    if not category:
        flash('Không tìm thấy danh mục.', 'danger')
        return redirect(url_for('admin.categories'))

    if request.method == 'POST':
        name = request.form.get('name')

        if not name:
            flash('Tên danh mục không được để trống.', 'danger')
            return render_template('admin/edit_category.html', category=category)

        existing = Category.get_by_name(name)
        if existing and existing.id != category.id:
            flash('Danh mục này đã tồn tại.', 'danger')
            return render_template('admin/edit_category.html', category=category)

        category.name = name
        if category.save():
            flash('Cập nhật danh mục thành công.', 'success')
            return redirect(url_for('admin.categories'))
        else:
            flash('Có lỗi xảy ra. Vui lòng thử lại.', 'danger')

    return render_template('admin/edit_category.html', category=category)


@admin.route('/categories/<int:category_id>/delete', methods=['POST'])
@admin_required
def delete_category(category_id):
    category = Category.get_by_id(category_id)
    if not category:
        flash('Không tìm thấy danh mục.', 'danger')
        return redirect(url_for('admin.categories'))

    products_count = Product.query.filter_by(category_id=category.id, is_deleted=False).count()
    if products_count > 0:
        flash(f'Không thể xóa danh mục này vì có {products_count} sản phẩm liên quan.', 'danger')
        return redirect(url_for('admin.categories'))

    category.is_deleted = True
    if category.save():
        flash('Xóa danh mục thành công.', 'success')
    else:
        flash('Có lỗi xảy ra. Vui lòng thử lại.', 'danger')

    return redirect(url_for('admin.categories'))


@admin.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():

    categories = Category.query.filter_by(is_deleted=False).all()

    if not categories:
        flash('Vui lòng tạo ít nhất một danh mục trước khi thêm sản phẩm.', 'warning')
        return redirect(url_for('admin.categories'))

    if request.method == 'POST':
        title = request.form.get('title')
        category_id = request.form.get('category_id')
        price = request.form.get('price')
        description = request.form.get('description')
        image = request.form.get('image')
        thumbnail = request.form.get('thumbnail')

        if not title or not category_id or not price:
            flash('Vui lòng điền đầy đủ thông tin bắt buộc.', 'danger')
            return render_template('admin/add_product.html', categories=categories)

        try:
            price = float(price)
            if price <= 0:
                raise ValueError()
        except ValueError:
            flash('Giá sản phẩm không hợp lệ.', 'danger')
            return render_template('admin/add_product.html', categories=categories)

        category = Category.get_by_id(int(category_id))
        if not category:
            flash('Danh mục không hợp lệ.', 'danger')
            return render_template('admin/add_product.html', categories=categories)

        product = Product(
            title=title,
            category_id=category.id,
            price=price,
            description=description,
            image=image,
            thumbnail=thumbnail
        )

        if product.save():
            flash('Thêm sản phẩm thành công.', 'success')
            return redirect(url_for('admin.products'))
        else:
            flash('Có lỗi xảy ra. Vui lòng thử lại.', 'danger')

    return render_template('admin/add_product.html', categories=categories)


@admin.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = Product.get_by_id(product_id)
    if not product:
        flash('Không tìm thấy sản phẩm.', 'danger')
        return redirect(url_for('admin.products'))

    categories = Category.query.filter_by(is_deleted=False).all()

    if request.method == 'POST':
        title = request.form.get('title')
        category_id = request.form.get('category_id')
        price = request.form.get('price')
        description = request.form.get('description')
        image = request.form.get('image')
        thumbnail = request.form.get('thumbnail')

        # Validate form data
        if not title or not category_id or not price:
            flash('Vui lòng điền đầy đủ thông tin bắt buộc.', 'danger')
            return render_template('admin/edit_product.html', product=product, categories=categories)

        try:
            price = float(price)
            if price <= 0:
                raise ValueError()
        except ValueError:
            flash('Giá sản phẩm không hợp lệ.', 'danger')
            return render_template('admin/edit_product.html', product=product, categories=categories)

        category = Category.get_by_id(int(category_id))
        if not category:
            flash('Danh mục không hợp lệ.', 'danger')
            return render_template('admin/edit_product.html', product=product, categories=categories)

        product.title = title
        product.category_id = category.id
        product.price = price
        product.description = description
        product.image = image
        product.thumbnail = thumbnail

        if product.save():
            flash('Cập nhật sản phẩm thành công.', 'success')
            return redirect(url_for('admin.products'))
        else:
            flash('Có lỗi xảy ra. Vui lòng thử lại.', 'danger')

    return render_template('admin/edit_product.html', product=product, categories=categories)


@admin.route('/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.get_by_id(product_id)
    if not product:
        flash('Không tìm thấy sản phẩm.', 'danger')
        return redirect(url_for('admin.products'))

    product.is_deleted = True
    if product.save():
        flash('Xóa sản phẩm thành công.', 'success')
    else:
        flash('Có lỗi xảy ra. Vui lòng thử lại.', 'danger')

    return redirect(url_for('admin.products'))


@admin.route('/settings')
@admin_required
def settings():
    roles = Role.query.filter_by(is_deleted=False).all()
    permissions = Permission.query.filter_by(is_deleted=False).all()

    return render_template('admin/settings.html', roles=roles, permissions=permissions)


@admin.route('/settings/roles/add', methods=['POST'])
@admin_required
def add_role():
    name = request.form.get('name')
    description = request.form.get('description', '')

    if not name:
        flash('Tên vai trò không được để trống.', 'danger')
        return redirect(url_for('admin.settings'))

    if Role.get_by_name(name):
        flash('Vai trò này đã tồn tại.', 'danger')
        return redirect(url_for('admin.settings'))

    role = Role(name=name, description=description)
    if role.save():
        flash('Thêm vai trò thành công.', 'success')
    else:
        flash('Có lỗi xảy ra. Vui lòng thử lại.', 'danger')

    return redirect(url_for('admin.settings'))


@admin.route('/settings/roles/<int:role_id>/edit', methods=['POST'])
@admin_required
def edit_role(role_id):
    role = Role.get_by_id(role_id)
    if not role:
        flash('Không tìm thấy vai trò.', 'danger')
        return redirect(url_for('admin.settings'))

    name = request.form.get('name')
    description = request.form.get('description', '')

    if not name:
        flash('Tên vai trò không được để trống.', 'danger')
        return redirect(url_for('admin.settings'))

    if role.name in ['Admin', 'User'] and role.name != name:
        flash('Không thể thay đổi tên vai trò mặc định.', 'danger')
        return redirect(url_for('admin.settings'))

    existing = Role.get_by_name(name)
    if existing and existing.id != role.id:
        flash('Vai trò này đã tồn tại.', 'danger')
        return redirect(url_for('admin.settings'))

    role.name = name
    role.description = description

    if role.save():
        flash('Cập nhật vai trò thành công.', 'success')
    else:
        flash('Có lỗi xảy ra. Vui lòng thử lại.', 'danger')

    return redirect(url_for('admin.settings'))


@admin.route('/settings/roles/<int:role_id>/delete', methods=['POST'])
@admin_required
def delete_role(role_id):
    role = Role.get_by_id(role_id)
    if not role:
        flash('Không tìm thấy vai trò.', 'danger')
        return redirect(url_for('admin.settings'))

    if role.name in ['Admin', 'User']:
        flash('Không thể xóa vai trò mặc định.', 'danger')
        return redirect(url_for('admin.settings'))

    users_count = User.query.filter_by(role_id=role.id, is_deleted=False).count()
    if users_count > 0:
        flash(f'Không thể xóa vai trò này vì có {users_count} người dùng đang sử dụng.', 'danger')
        return redirect(url_for('admin.settings'))

    role.is_deleted = True
    if role.save():
        flash('Xóa vai trò thành công.', 'success')
    else:
        flash('Có lỗi xảy ra. Vui lòng thử lại.', 'danger')

    return redirect(url_for('admin.settings'))


@admin.route('/settings/permissions/add', methods=['POST'])
@admin_required
def add_permission():
    name = request.form.get('name')
    description = request.form.get('description', '')

    if not name:
        flash('Tên quyền không được để trống.', 'danger')
        return redirect(url_for('admin.settings'))

    if Permission.get_by_name(name):
        flash('Quyền này đã tồn tại.', 'danger')
        return redirect(url_for('admin.settings'))

    permission = Permission(name=name, description=description)
    if permission.save():
        flash('Thêm quyền thành công.', 'success')
    else:
        flash('Có lỗi xảy ra. Vui lòng thử lại.', 'danger')

    return redirect(url_for('admin.settings'))


@admin.route('/settings/permissions/<int:permission_id>/edit', methods=['POST'])
@admin_required
def edit_permission(permission_id):
    permission = Permission.get_by_id(permission_id)
    if not permission:
        flash('Không tìm thấy quyền.', 'danger')
        return redirect(url_for('admin.settings'))

    name = request.form.get('name')
    description = request.form.get('description', '')

    if not name:
        flash('Tên quyền không được để trống.', 'danger')
        return redirect(url_for('admin.settings'))

    existing = Permission.get_by_name(name)
    if existing and existing.id != permission.id:
        flash('Quyền này đã tồn tại.', 'danger')
        return redirect(url_for('admin.settings'))

    permission.name = name
    permission.description = description

    if permission.save():
        flash('Cập nhật quyền thành công.', 'success')
    else:
        flash('Có lỗi xảy ra. Vui lòng thử lại.', 'danger')

    return redirect(url_for('admin.settings'))


@admin.route('/settings/permissions/<int:permission_id>/delete', methods=['POST'])
@admin_required
def delete_permission(permission_id):
    permission = Permission.get_by_id(permission_id)
    if not permission:
        flash('Không tìm thấy quyền.', 'danger')
        return redirect(url_for('admin.settings'))

    roles = Role.query.filter_by(is_deleted=False).all()
    for role in roles:
        if permission in role.permissions:
            role.permissions.remove(permission)

    permission.is_deleted = True

    try:
        db.session.commit()
        flash('Xóa quyền thành công.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting permission: {str(e)}")
        flash('Có lỗi xảy ra. Vui lòng thử lại.', 'danger')

    return redirect(url_for('admin.settings'))


@admin.route('/settings/roles/<int:role_id>/permissions', methods=['GET', 'POST'])
@admin_required
def role_permissions(role_id):
    role = Role.get_by_id(role_id)
    if not role:
        flash('Không tìm thấy vai trò.', 'danger')
        return redirect(url_for('admin.settings'))

    if request.method == 'POST':
        permission_ids = request.form.getlist('permissions')

        role.permissions = []

        if permission_ids:
            permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
            role.permissions = permissions

        if role.save():
            flash('Cập nhật quyền thành công.', 'success')
        else:
            flash('Có lỗi xảy ra. Vui lòng thử lại.', 'danger')

    permissions = Permission.query.filter_by(is_deleted=False).all()
    return render_template('admin/role_permissions.html', role=role, permissions=permissions)