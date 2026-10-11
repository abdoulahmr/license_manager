from flask import Blueprint, render_template
from routes.auth import login_required
from repositories import activations

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    return render_template(
        'dashboard.html',
        counts=activations.counts(),
        recent=activations.recent(20),
        by_country=activations.by_country(30),
        timeseries=activations.timeseries(30),
    )