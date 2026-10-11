from functools import wraps
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from config import Config

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not session.get('user'):
            flash('Please log in.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return wrap

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username', '')
        p = request.form.get('password', '')
        if u == Config.ADMIN_USERNAME and p == Config.ADMIN_PASSWORD:
            session['user'] = u
            nxt = request.args.get('next') or url_for('dashboard.index')
            return redirect(nxt)
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    return redirect(url_for('auth.login'))