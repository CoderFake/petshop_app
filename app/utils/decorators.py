from functools import wraps
from flask import session, redirect, url_for, flash, request, abort, g
from app.models import User


def current_user():
    if session.get('user_id') is None:
        return None

    if not hasattr(g, 'user'):
        g.user = User.get_by_id(session.get('user_id'))

    return g.user


def login_required(view):

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get('user_id') is None:
            flash('Vui lòng đăng nhập để tiếp tục.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


def anonymous_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get('user_id') is not None:
            return redirect(url_for('main.index'))
        return view(*args, **kwargs)

    return wrapped_view


def role_required(role_name):
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if session.get('user_id') is None:
                flash('Vui lòng đăng nhập để tiếp tục.', 'warning')
                return redirect(url_for('auth.login', next=request.path))

            if session.get('user_role') != role_name and session.get('user_role') != 'Admin':
                flash('Bạn không có quyền truy cập trang này.', 'danger')
                abort(403)

            return view(*args, **kwargs)

        return wrapped_view

    return decorator


def admin_required(view):
    return role_required('Admin')(view)


def permission_required(permission_name):

    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if session.get('user_id') is None:
                flash('Vui lòng đăng nhập để tiếp tục.', 'warning')
                return redirect(url_for('auth.login', next=request.path))

            user = User.get_by_id(session.get('user_id'))
            if not user:
                session.clear()
                flash('Phiên đăng nhập không hợp lệ. Vui lòng đăng nhập lại.', 'warning')
                return redirect(url_for('auth.login'))

            if not user.has_permission(permission_name) and session.get('user_role') != 'Admin':
                flash('Bạn không có quyền thực hiện hành động này.', 'danger')
                abort(403)

            return view(*args, **kwargs)

        return wrapped_view

    return decorator