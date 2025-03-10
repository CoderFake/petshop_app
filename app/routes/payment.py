from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app, jsonify
from app.extensions import db
from app.models import Order, User, OrderDetail, Product
from app.utils.decorators import login_required, current_user
from app.utils.vnpay import VNPay
from app.utils.email import send_order_confirmation_email
import json
from datetime import datetime


payment = Blueprint('payment', __name__)


@payment.route('/checkout', methods=['GET', 'POST'])
def checkout():

    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        payment_method = request.form.get('payment_method')
        notes = request.form.get('notes', '')

        if not fullname or not email or not phone or not address:
            flash('Vui lòng điền đầy đủ thông tin giao hàng.', 'danger')
            return redirect(url_for('payment.checkout'))

        cart = session.get('cart', {})

        if not cart:
            flash('Giỏ hàng của bạn đang trống.', 'warning')
            return redirect(url_for('main.cart'))

        total_price = 0
        order_items = []

        for product_id, item in cart.items():
            product = Product.get_by_id(int(product_id))
            if not product:
                continue

            quantity = item.get('quantity', 1)
            price = float(product.price)
            subtotal = price * quantity

            total_price += subtotal

            order_items.append({
                'product_id': product.id,
                'quantity': quantity,
                'price': price
            })

        user_id = session.get('user_id')
        user = User.get_by_id(user_id) if user_id else None

        order = Order(
            user_id=user_id if user_id else None,
            total_price=total_price,
            fullname=fullname,
            email=email,
            phone=phone,
            address=address,
            payment_method=payment_method,
            notes=notes,
            status='pending',
            payment_status='pending'
        )

        try:
            db.session.add(order)
            db.session.commit()

            for item in order_items:
                order_detail = OrderDetail(
                    order_id=order.id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    price=item['price']
                )
                db.session.add(order_detail)

            db.session.commit()

            try:
                if not user:
                    temp_user = type('obj', (object,), {
                        'name': fullname,
                        'email': email
                    })
                    send_order_confirmation_email(temp_user, order)
                else:
                    send_order_confirmation_email(user, order)
            except Exception as e:
                current_app.logger.error(f"Failed to send order confirmation email: {str(e)}")

            if not user_id:
                anonymous_orders = session.get('anonymous_orders', [])
                anonymous_orders.append(order.id)
                session['anonymous_orders'] = anonymous_orders

            session['cart'] = {}

            if payment_method == 'vnpay':
                vnpay = VNPay()
                payment_url = vnpay.get_payment_url(
                    order_id=order.id,
                    amount=total_price,
                    order_desc=f"Thanh toán đơn hàng #{order.id} tại Pet Shop"
                )
                return redirect(payment_url)
            else:
                flash('Đặt hàng thành công! Cảm ơn bạn đã mua sắm tại Pet Shop.', 'success')
                return redirect(url_for('payment.success', order_id=order.id))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Order creation error: {str(e)}")
            flash('Đã có lỗi xảy ra khi xử lý đơn hàng. Vui lòng thử lại sau.', 'danger')
            return redirect(url_for('payment.checkout'))

    cart = session.get('cart', {})

    if not cart:
        flash('Giỏ hàng của bạn đang trống.', 'warning')
        return redirect(url_for('main.cart'))

    cart_items = []
    total_price = 0

    for product_id, item in cart.items():
        product = Product.get_by_id(int(product_id))
        if not product:
            continue

        quantity = item.get('quantity', 1)
        price = float(product.price)
        subtotal = price * quantity

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'price': price,
            'subtotal': subtotal
        })

        total_price += subtotal

    user = current_user()

    return render_template('payment/checkout.html',
                           cart_items=cart_items,
                           total_price=total_price,
                           user=user)


@payment.route('/vnpay-return', methods=['GET'])
def vnpay_return():
    vnp_params = request.args.to_dict()
    vnpay = VNPay()
    is_valid, order_id, amount, response_code = vnpay.validate_response(vnp_params)

    if not is_valid:
        flash('Xác thực thanh toán thất bại. Vui lòng liên hệ với chúng tôi nếu bạn đã thanh toán.', 'danger')
        return redirect(url_for('main.index'))

    try:
        order_id = int(order_id)
        order = Order.get_by_id(order_id)

        if not order:
            flash('Không tìm thấy đơn hàng. Vui lòng liên hệ với chúng tôi nếu bạn đã thanh toán.', 'danger')
            return redirect(url_for('main.index'))

        if response_code == '00':
            order.payment_status = 'paid'
            order.transaction_id = vnp_params.get('vnp_TransactionNo', '')
            order.status = 'processing'
            db.session.commit()

            flash('Thanh toán thành công! Cảm ơn bạn đã mua sắm tại Pet Shop.', 'success')
            return redirect(url_for('payment.success', order_id=order.id))
        else:
            flash(
                f'Thanh toán thất bại. Mã lỗi: {response_code}. Vui lòng thử lại hoặc chọn phương thức thanh toán khác.',
                'danger')

            if session.get('user_id'):
                return redirect(url_for('main.orders'))
            else:
                return redirect(url_for('payment.track_order', order_id=order.id))

    except Exception as e:
        current_app.logger.error(f"VNPay return error: {str(e)}")
        flash('Đã có lỗi xảy ra khi xử lý thanh toán. Vui lòng liên hệ với chúng tôi nếu bạn đã thanh toán.', 'danger')
        return redirect(url_for('main.index'))


@payment.route('/success/<int:order_id>')
def success(order_id):
    order = Order.get_by_id(order_id)

    if not order:
        flash('Không tìm thấy đơn hàng.', 'danger')
        return redirect(url_for('main.index'))

    user_id = session.get('user_id')
    anonymous_orders = session.get('anonymous_orders', [])

    if user_id and order.user_id != user_id and order.id not in anonymous_orders:
        flash('Bạn không có quyền truy cập đơn hàng này.', 'danger')
        return redirect(url_for('main.index'))

    if not user_id and order.id not in anonymous_orders:
        flash('Bạn không có quyền truy cập đơn hàng này.', 'danger')
        return redirect(url_for('main.index'))

    return render_template('payment/success.html', order=order)


@payment.route('/track-order', methods=['GET', 'POST'])
def track_order():
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        email = request.form.get('email')

        if not order_id or not email:
            flash('Vui lòng điền đầy đủ thông tin.', 'danger')
            return render_template('payment/track_order.html')

        try:
            order_id = int(order_id)
            order = Order.query.filter_by(id=order_id, email=email, is_deleted=False).first()

            if not order:
                flash('Không tìm thấy đơn hàng với thông tin cung cấp.', 'danger')
                return render_template('payment/track_order.html')

            anonymous_orders = session.get('anonymous_orders', [])
            if order.id not in anonymous_orders:
                anonymous_orders.append(order.id)
                session['anonymous_orders'] = anonymous_orders

            return redirect(url_for('payment.order_detail', order_id=order.id))

        except ValueError:
            flash('Mã đơn hàng không hợp lệ.', 'danger')
            return render_template('payment/track_order.html')

    return render_template('payment/track_order.html')


@payment.route('/order-detail/<int:order_id>')
def order_detail(order_id):
    order = Order.get_by_id(order_id)

    if not order:
        flash('Không tìm thấy đơn hàng.', 'danger')
        return redirect(url_for('main.index'))

    user_id = session.get('user_id')
    anonymous_orders = session.get('anonymous_orders', [])

    if user_id and order.user_id != user_id and order.id not in anonymous_orders:
        flash('Bạn không có quyền truy cập đơn hàng này.', 'danger')
        return redirect(url_for('main.index'))

    if not user_id and order.id not in anonymous_orders:
        flash('Bạn không có quyền truy cập đơn hàng này.', 'danger')
        return redirect(url_for('main.index'))

    return render_template('payment/order_detail.html', order=order)


@payment.route('/cancel/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    order = Order.get_by_id(order_id)

    if not order:
        flash('Không tìm thấy đơn hàng.', 'danger')
        return redirect(url_for('main.index'))

    user_id = session.get('user_id')
    anonymous_orders = session.get('anonymous_orders', [])

    if user_id and order.user_id != user_id and order.id not in anonymous_orders:
        flash('Bạn không có quyền hủy đơn hàng này.', 'danger')
        return redirect(url_for('main.index'))

    if not user_id and order.id not in anonymous_orders:
        flash('Bạn không có quyền hủy đơn hàng này.', 'danger')
        return redirect(url_for('payment.track_order'))

    if order.status in ['shipped', 'delivered']:
        flash('Không thể hủy đơn hàng đã vận chuyển hoặc giao hàng.', 'danger')
        if user_id:
            return redirect(url_for('main.order_detail', order_id=order_id))
        else:
            return redirect(url_for('payment.order_detail', order_id=order_id))

    if order.cancel():
        flash('Đơn hàng đã được hủy thành công.', 'success')
    else:
        flash('Không thể hủy đơn hàng. Vui lòng thử lại sau.', 'danger')

    if user_id:
        return redirect(url_for('main.order_detail', order_id=order_id))
    else:
        return redirect(url_for('payment.order_detail', order_id=order_id))