"""
Main routes for the Pet Shop application.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app.extensions import db

# Create blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/products')
def products():
    return render_template('products.html')

@main.route('/product/<int:product_id>')
def product_detail(product_id):
    return render_template('product_detail.html', product_id=product_id)

@main.route('/category/<int:category_id>')
def category(category_id):
    return render_template('category.html', category_id=category_id)

@main.route('/cart')
def cart():
    return render_template('cart.html')

@main.route('/checkout')
def checkout():
    return render_template('checkout.html')