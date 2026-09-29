from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.services import dashboard_service

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("", methods=["GET"])
@login_required
def index():
    metrics = dashboard_service.get_dashboard_metrics(current_user)
    return render_template("dashboard/index.html", metrics=metrics)
