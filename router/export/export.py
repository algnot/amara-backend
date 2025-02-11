from flask import Blueprint
from router.export.student import export_student_app

export_app = Blueprint("export", __name__, url_prefix="/export")

export_app.register_blueprint(export_student_app)
