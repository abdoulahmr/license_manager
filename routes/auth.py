from functools import wraps
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.utils import redirect as _redirect  # not strictly needed
from config import Config

auth_bp = Blueprint('auth', __name__)


def _safe_next(next_url):
    """Prevent open-redirect attacks: only allow relative paths on this site."""
    if not next_url:
        return None
    # Must start with single slash, not protocol-relative '//evil.com' or 'http://...'
    if next_url.startswith('/') and not next_url.startswith('//'):
        return next_url
    return None


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
    # Already authenticated → send to dashboard (or wherever ?next= points)
    if session.get('user'):
        nxt = _safe_next(request.args.get('next')) or url_for('dashboard.index')
        return redirect(nxt)

    if request.method == 'POST':
        u = request.form.get('username', '')
        p = request.form.get('password', '')
        if u == Config.ADMIN_USERNAME and p == Config.ADMIN_PASSWORD:
            session['user'] = u
            nxt = _safe_next(request.args.get('next')) or url_for('dashboard.index')
            return redirect(nxt)
        flash('Invalid credentials', 'error')
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    return redirect(url_for('auth.login'))