from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from repositories import products, licenses, activations

licenses_bp = Blueprint('licenses', __name__)

@licenses_bp.route('/')
@login_required
def list():
    return render_template('licenses/list.html', licenses=licenses.list_licenses())

@licenses_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        try:
            lic_id, key = licenses.create_license(
                int(request.form['product_id']),
                request.form['customer_name'],
                request.form.get('customer_email', ''),
                request.form.get('license_type', 'Professional'),
                request.form.get('notes', ''),
            )
            flash(f'License created: {key}', 'success')
            return redirect(url_for('licenses.history', lid=lic_id))
        except Exception as e:
            flash(f'Error: {e}', 'error')
    return render_template('licenses/form.html',
                           products=products.list_products(), license=None)

@licenses_bp.route('/<int:lid>')
@login_required
def history(lid):
    lic = licenses.get_license(lid)
    if not lic:
        flash('License not found', 'error')
        return redirect(url_for('licenses.list'))
    history_rows = activations.list_for_license(lid)
    return render_template('licenses/history.html',
                           license=lic, history=history_rows)

@licenses_bp.route('/<int:lid>/edit', methods=['GET', 'POST'])
@login_required
def edit(lid):
    lic = licenses.get_license(lid)
    if not lic:
        flash('License not found', 'error')
        return redirect(url_for('licenses.list'))
    if request.method == 'POST':
        licenses.update_license(
            lid,
            request.form['customer_name'],
            request.form.get('customer_email', ''),
            request.form.get('license_type', 'Professional'),
            request.form.get('notes', ''),
            request.form.get('status', lic['status']),
        )
        flash('License updated.', 'success')
        return redirect(url_for('licenses.history', lid=lid))
    return render_template('licenses/form.html',
                           products=products.list_products(), license=lic)

@licenses_bp.route('/<int:lid>/delete', methods=['POST'])
@login_required
def delete(lid):
    try:
        licenses.delete_license(lid)
        flash('License deleted.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('licenses.list'))

@licenses_bp.route('/<int:lid>/reset', methods=['POST'])
@login_required
def reset(lid):
    licenses.reset_activation(lid)
    activations.log_activation(lid, 'reset', {}, success=True, reason='Manual reset by admin')
    flash('Activation reset. License can now be activated on a new machine.', 'success')
    return redirect(url_for('licenses.history', lid=lid))

@licenses_bp.route('/<int:lid>/revoke', methods=['POST'])
@login_required
def revoke(lid):
    licenses.revoke_license(lid)
    activations.log_activation(lid, 'revoke', {}, success=True, reason='Manual revoke by admin')
    flash('License revoked.', 'warning')
    return redirect(url_for('licenses.history', lid=lid))