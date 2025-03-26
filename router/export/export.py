from flask import Blueprint
from router.export.certificate import export_certificate_app
from router.export.course import export_course_app
from router.export.sale_person import export_sale_person_app
from router.export.student import export_student_app

export_app = Blueprint("export", __name__, url_prefix="/export")

export_app.register_blueprint(export_student_app)
export_app.register_blueprint(export_certificate_app)
export_app.register_blueprint(export_course_app)
export_app.register_blueprint(export_sale_person_app)
