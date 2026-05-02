from flask import Blueprint

from router.dashboard.get_chart_course_summary import get_chart_course_summary_app
from router.dashboard.get_chart_month_summary import get_chart_month_summary_app
from router.dashboard.get_summary import get_summary_app

dashboard_app = Blueprint("dashboard", __name__, url_prefix="/dashboard")

dashboard_app.register_blueprint(get_summary_app)
dashboard_app.register_blueprint(get_chart_month_summary_app)
dashboard_app.register_blueprint(get_chart_course_summary_app)

