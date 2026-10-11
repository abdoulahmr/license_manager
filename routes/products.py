from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from repositories import products

products_bp = Blueprint('products', __name__)

@products_bp.route('/')
@login_required
def list():
    return render_template('products/list.html', products=products.list_products())

@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        try:
            products.create_product(
                name=request.form['name'],
                code_prefix=request.form['code_prefix'],
                description=request.form.get('description', ''),
                version=request.form.get('version', '1.0'),
            )
            flash(f'Product "{request.form["name"]}" created.', 'success')
            return redirect(url_for('products.list'))
        except Exception as e:
            db.session.rollback() if False else None
            flash(f'Error: {e}', 'error')
    return render_template('products/form.html', product=None)

@products_bp.route('/<int:pid>/edit', methods=['GET', 'POST'])
@login_required
def edit(pid):
    product = products.get_product(pid)
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('products.list'))
    if request.method == 'POST':
        try:
            products.update_product(
                pid,
                request.form['name'],
                request.form['code_prefix'],
                request.form.get('description', ''),
                request.form.get('version', '1.0'),
            )
            flash('Product updated.', 'success')
            return redirect(url_for('products.list'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
    return render_template('products/form.html', product=product)

@products_bp.route('/<int:pid>/delete', methods=['POST'])
@login_required
def delete(pid):
    try:
        products.delete_product(pid)
        flash('Product deleted.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('products.list'))