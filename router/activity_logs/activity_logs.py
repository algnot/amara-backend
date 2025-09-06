from flask import Blueprint
from router.activity_logs.get_activity_logs import get_activity_logs_app

activity_log_app = Blueprint("activity_log", __name__, url_prefix="/activity-logs")

activity_log_app.register_blueprint(get_activity_logs_app)
