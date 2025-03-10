from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, g
from app.extensions import db
from app.models import Category, Product, Feedback, User, Order
from sqlalchemy import desc, func
from flask_login import current_user

main = Blueprint('main', __name__)


@main.before_request
def load_categories():
    g.categories = Category.query.filter_by(is_deleted=False).all()


@main.route('/')
def index():
    categories = Category.query.filter_by(is_deleted=False).all()

    featured_products = Product.query.filter_by(is_deleted=False) \
        .order_by(desc(Product.created_at)) \
        .limit(8).all()

    return render_template('index.html',
                           categories=categories,
                           featured_products=featured_products)


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message = request.form.get('message')

        flash('Cảm ơn bạn đã liên hệ với chúng tôi! Chúng tôi sẽ phản hồi sớm nhất có thể.', 'success')
        return redirect(url_for('main.contact'))

    return render_template('contact.html')


@main.route('/service')
def service():
    """Services page"""
    return render_template('service.html')


@main.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    per_page = 12

    search_query = request.args.get('search', '')
    category_id = request.args.get('category_id', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort = request.args.get('sort', 'newest')

    query = Product.query.filter_by(is_deleted=False)

    if search_query:
        query = query.filter(Product.title.ilike(f'%{search_query}%'))

    if category_id:
        query = query.filter_by(category_id=category_id)
        category = Category.get_by_id(category_id)
    else:
        category = None

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'name_asc':
        query = query.order_by(Product.title.asc())
    elif sort == 'name_desc':
        query = query.order_by(Product.title.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    products = query.paginate(page=page, per_page=per_page)

    all_categories = Category.query.filter_by(is_deleted=False).all()

    return render_template('products.html',
                           products=products,
                           category=category,
                           all_categories=all_categories,
                           search_query=search_query)


@main.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.get_by_id(product_id)

    if not product:
        flash('Sản phẩm không tồn tại hoặc đã bị xóa.', 'danger')
        return redirect(url_for('main.products'))

    # Get related products from the same category
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_deleted == False
    ).limit(4).all()

    return render_template('product_detail.html',
                           product=product,
                           related_products=related_products,
                           current_user=g.user if hasattr(g, 'user') else None)


@main.route('/category/<int:category_id>')
def category(category_id):
    category = Category.get_by_id(category_id)

    if not category:
        flash('Danh mục không tồn tại hoặc đã bị xóa.', 'danger')
        return redirect(url_for('main.products'))

    page = request.args.get('page', 1, type=int)
    per_page = 12

    products = Product.query.filter_by(
        category_id=category_id,
        is_deleted=False
    ).paginate(page=page, per_page=per_page)

    return render_template('category.html',
                           category=category,
                           products=products)


@main.route('/cart')
def cart():
    cart = session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, item in cart.items():
        product = Product.get_by_id(int(product_id))
        if product:
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

    return render_template('cart.html',
                           cart_items=cart_items,
                           total_price=total_price)


@main.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    buy_now = request.form.get('buy_now')

    if not product_id:
        return jsonify({'success': False, 'message': 'Không tìm thấy sản phẩm'})

    product = Product.get_by_id(int(product_id))
    if not product:
        return jsonify({'success': False, 'message': 'Không tìm thấy sản phẩm'})

    cart = session.get('cart', {})

    if product_id in cart:
        cart[product_id]['quantity'] += quantity
    else:
        cart[product_id] = {
            'quantity': quantity
        }

    session['cart'] = cart
    cart_count = sum(item['quantity'] for item in cart.values())

    if buy_now:
        return jsonify({
            'success': True,
            'cart_count': cart_count,
            'redirect': url_for('payment.checkout')
        })

    return jsonify({
        'success': True,
        'cart_count': cart_count
    })


@main.route('/update-cart', methods=['POST'])
def update_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))

    if not product_id:
        return jsonify({'success': False, 'message': 'Không tìm thấy sản phẩm'})

    cart = session.get('cart', {})

    if product_id in cart:
        cart[product_id]['quantity'] = quantity
        session['cart'] = cart

        product = Product.get_by_id(int(product_id))
        if product:
            subtotal = float(product.price) * quantity

            total_price = sum(
                float(Product.get_by_id(int(pid)).price) * item['quantity']
                for pid, item in cart.items()
                if Product.get_by_id(int(pid))
            )

            cart_count = sum(item['quantity'] for item in cart.values())

            return jsonify({
                'success': True,
                'item_subtotal': '{:,.0f}đ'.format(subtotal),
                'total_price': '{:,.0f}đ'.format(total_price),
                'cart_count': cart_count
            })

    return jsonify({'success': False, 'message': 'Cập nhật giỏ hàng thất bại'})


@main.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    product_id = request.form.get('product_id')

    if not product_id:
        return jsonify({'success': False, 'message': 'Không tìm thấy sản phẩm'})

    cart = session.get('cart', {})

    if product_id in cart:
        del cart[product_id]
        session['cart'] = cart

        total_price = sum(
            float(Product.get_by_id(int(pid)).price) * item['quantity']
            for pid, item in cart.items()
            if Product.get_by_id(int(pid))
        )

        cart_count = sum(item['quantity'] for item in cart.values())

        return jsonify({
            'success': True,
            'total_price': '{:,.0f}đ'.format(total_price),
            'cart_count': cart_count
        })

    return jsonify({'success': False, 'message': 'Xóa sản phẩm thất bại'})


@main.route('/add-review/<int:product_id>', methods=['POST'])
def add_review(product_id):
    product = Product.get_by_id(product_id)

    if not product:
        flash('Sản phẩm không tồn tại hoặc đã bị xóa.', 'danger')
        return redirect(url_for('main.products'))

    name = request.form.get('name')
    email = request.form.get('email')
    rating = int(request.form.get('rating', 5))
    comment = request.form.get('comment')

    user_id = session.get('user_id')

    feedback = Feedback(
        name=name,
        email=email,
        user_id=user_id,
        product_id=product_id,
        rating=rating,
        comment=comment
    )

    if feedback.save():
        flash('Cảm ơn bạn đã đánh giá sản phẩm!', 'success')
    else:
        flash('Có lỗi xảy ra khi gửi đánh giá. Vui lòng thử lại.', 'danger')

    return redirect(url_for('main.product_detail', product_id=product_id))


@main.route('/orders')
def orders():
    user_id = session.get('user_id')

    if not user_id:
        flash('Vui lòng đăng nhập để xem đơn hàng của bạn.', 'warning')
        return redirect(url_for('auth.login', next=request.path))

    page = request.args.get('page', 1, type=int)
    per_page = 10

    orders = Order.query.filter_by(
        user_id=user_id,
        is_deleted=False
    ).order_by(
        Order.created_at.desc()
    ).paginate(page=page, per_page=per_page)

    return render_template('orders.html', orders=orders)


@main.route('/order/<int:order_id>')
def order_detail(order_id):
    user_id = session.get('user_id')

    if not user_id:
        flash('Vui lòng đăng nhập để xem chi tiết đơn hàng.', 'warning')
        return redirect(url_for('auth.login', next=request.path))

    order = Order.query.filter_by(
        id=order_id,
        user_id=user_id,
        is_deleted=False
    ).first()

    if not order:
        flash('Không tìm thấy đơn hàng hoặc bạn không có quyền xem đơn hàng này.', 'danger')
        return redirect(url_for('main.orders'))

    return render_template('order_detail.html', order=order)


@main.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')


@main.route('/addresses')
def addresses():
    return render_template('addresses.html')