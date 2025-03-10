from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from app.extensions import db
from app.models import User, Role, Order
from app.utils.email import send_verification_email
from app.utils.decorators import login_required, anonymous_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
import functools

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form

        user = User.get_by_email(email)

        if user and user.verify_password(password):
            if not user.is_active:
                flash('Tài khoản chưa được kích hoạt. Vui lòng kiểm tra email của bạn.', 'warning')
                return render_template('auth/login.html')

            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['user_role'] = user.role.name if user.role else 'User'

            if remember:
                session.permanent = True

            anonymous_orders = session.get('anonymous_orders', [])
            if anonymous_orders:
                for order_id in anonymous_orders:
                    order = Order.get_by_id(order_id)
                    if order and not order.user_id:
                        order.user_id = user.id
                session.pop('anonymous_orders', None)
                db.session.commit()

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('Email hoặc mật khẩu không chính xác.', 'danger')

    return render_template('auth/login.html')


@auth.route('/register', methods=['GET', 'POST'])
@anonymous_required
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        error = None
        if not name or not email or not password:
            error = 'Vui lòng điền đầy đủ thông tin.'
        elif User.get_by_email(email):
            error = 'Email này đã được đăng ký.'
        elif password != confirm_password:
            error = 'Mật khẩu không khớp.'
        elif len(password) < 8:
            error = 'Mật khẩu phải có ít nhất 8 ký tự.'

        if error:
            flash(error, 'danger')
            return render_template('auth/register.html')

        user_role = Role.get_by_name('User')
        if not user_role:
            user_role = Role(name='User')
            db.session.add(user_role)
            db.session.commit()

        user = User(
            name=name,
            email=email,
            role_id=user_role.id,
            is_active=False
        )
        user.password = password

        verification_token = user.generate_verification_token()

        try:
            db.session.add(user)
            db.session.commit()

            verification_url = url_for(
                'auth.verify_email',
                token=verification_token,
                _external=True
            )
            send_verification_email(user, verification_url)

            flash('Tài khoản đã được tạo! Vui lòng kiểm tra email để xác thực tài khoản.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {str(e)}")
            flash('Đã có lỗi xảy ra. Vui lòng thử lại sau.', 'danger')

    return render_template('auth/register.html')


@auth.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    if session.get('user_id'):
        return redirect(url_for('main.index'))

    user = User.get_by_token(token)

    if user is None:
        flash('Liên kết xác thực không hợp lệ hoặc đã hết hạn.', 'danger')
        return redirect(url_for('auth.login'))

    if user.verify_account(token):
        db.session.commit()
        flash('Tài khoản của bạn đã được xác thực thành công! Bạn có thể đăng nhập ngay bây giờ.', 'success')
    else:
        flash('Liên kết xác thực không hợp lệ hoặc đã hết hạn.', 'danger')

    return redirect(url_for('auth.login'))


@auth.route('/logout')
def logout():
    cart = session.get('cart', {})
    anonymous_orders = session.get('anonymous_orders', [])

    session.clear()

    session['cart'] = cart
    if anonymous_orders:
        session['anonymous_orders'] = anonymous_orders

    flash('Bạn đã đăng xuất thành công.', 'info')
    return redirect(url_for('main.index'))


@auth.route('/profile')
@login_required
def profile():
    user = current_user()

    if not user:
        session.clear()
        flash('Phiên đăng nhập không hợp lệ. Vui lòng đăng nhập lại.', 'warning')
        return redirect(url_for('auth.login'))

    return render_template('auth/profile.html', user=user)


@auth.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = current_user()

    if not user:
        session.clear()
        flash('Phiên đăng nhập không hợp lệ. Vui lòng đăng nhập lại.', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        avatar = request.form.get('avatar')

        if not name:
            flash('Họ tên không được để trống.', 'danger')
        else:
            user.name = name
            user.phone = phone
            user.address = address
            user.avatar = avatar

            if user.save():
                # Update session data
                session['user_name'] = user.name
                flash('Cập nhật thông tin thành công!', 'success')
                return redirect(url_for('auth.profile'))
            else:
                flash('Đã có lỗi xảy ra. Vui lòng thử lại sau.', 'danger')

    return render_template('auth/edit_profile.html', user=user)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    user = current_user()

    if not user:
        session.clear()
        flash('Phiên đăng nhập không hợp lệ. Vui lòng đăng nhập lại.', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_password or not new_password or not confirm_password:
            flash('Vui lòng điền đầy đủ thông tin.', 'danger')
        elif not user.verify_password(current_password):
            flash('Mật khẩu hiện tại không chính xác.', 'danger')
        elif new_password != confirm_password:
            flash('Mật khẩu mới không khớp.', 'danger')
        elif len(new_password) < 8:
            flash('Mật khẩu mới phải có ít nhất 8 ký tự.', 'danger')
        else:
            user.password = new_password

            if user.save():
                flash('Mật khẩu đã được thay đổi thành công!', 'success')
                return redirect(url_for('auth.profile'))
            else:
                flash('Đã có lỗi xảy ra. Vui lòng thử lại sau.', 'danger')

    return render_template('auth/change_password.html')


@auth.route('/resend-verification', methods=['GET', 'POST'])
@anonymous_required
def resend_verification():
    """Resend verification email"""
    if request.method == 'POST':
        email = request.form.get('email')

        if not email:
            flash('Vui lòng nhập email của bạn.', 'danger')
            return render_template('auth/resend_verification.html')

        user = User.get_by_email(email)

        if not user:
            flash('Không tìm thấy tài khoản với email này.', 'danger')
            return render_template('auth/resend_verification.html')

        if user.is_active:
            flash('Tài khoản này đã được kích hoạt. Vui lòng đăng nhập.', 'info')
            return redirect(url_for('auth.login'))

        verification_token = user.generate_verification_token()
        db.session.commit()

        verification_url = url_for(
            'auth.verify_email',
            token=verification_token,
            _external=True
        )
        if send_verification_email(user, verification_url):
            flash('Email xác thực đã được gửi lại. Vui lòng kiểm tra hộp thư của bạn.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Không thể gửi email xác thực. Vui lòng thử lại sau.', 'danger')

    return render_template('auth/resend_verification.html')


@auth.route('/forgot-password', methods=['GET', 'POST'])
@anonymous_required
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')

        if not email:
            flash('Vui lòng nhập email của bạn.', 'danger')
            return render_template('auth/forgot_password.html')

        user = User.get_by_email(email)

        if not user:
            flash('Nếu email này được đăng ký, bạn sẽ nhận được hướng dẫn đặt lại mật khẩu.', 'info')
            return render_template('auth/forgot_password.html')

        reset_token = user.generate_verification_token()
        db.session.commit()

        reset_url = url_for(
            'auth.reset_password',
            token=reset_token,
            _external=True
        )
        from app.utils.email import send_password_reset_email
        if send_password_reset_email(user, reset_url):
            flash('Email hướng dẫn đặt lại mật khẩu đã được gửi. Vui lòng kiểm tra hộp thư của bạn.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Không thể gửi email đặt lại mật khẩu. Vui lòng thử lại sau.', 'danger')

    return render_template('auth/forgot_password.html')


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
@anonymous_required
def reset_password(token):
    user = User.get_by_token(token)

    if user is None or user.token_expiry is None or user.token_expiry < datetime.utcnow():
        flash('Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not new_password or not confirm_password:
            flash('Vui lòng điền đầy đủ thông tin.', 'danger')
        elif new_password != confirm_password:
            flash('Mật khẩu không khớp.', 'danger')
        elif len(new_password) < 8:
            flash('Mật khẩu phải có ít nhất 8 ký tự.', 'danger')
        else:
            user.password = new_password
            user.verification_token = None
            user.token_expiry = None

            if user.save():
                flash('Mật khẩu đã được đặt lại thành công! Bạn có thể đăng nhập ngay bây giờ.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Đã có lỗi xảy ra. Vui lòng thử lại sau.', 'danger')

    return render_template('auth/reset_password.html', token=token)