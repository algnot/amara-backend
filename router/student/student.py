from flask import Blueprint

from router.student.add_student import add_student_app
from router.student.generate_user_student import generate_user_student_app
from router.student.get_student import get_student_app
from router.student.update_student import update_student_app

student_app = Blueprint("student", __name__, url_prefix="/student")

student_app.register_blueprint(add_student_app)
student_app.register_blueprint(get_student_app)
student_app.register_blueprint(update_student_app)
student_app.register_blueprint(generate_user_student_app)
