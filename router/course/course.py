from flask import Blueprint
from router.course.add_course import add_course_app
from router.course.get_course import get_course_app
from router.course.update_course import update_course_app

course_app = Blueprint("course", __name__, url_prefix="/course")

course_app.register_blueprint(add_course_app)
course_app.register_blueprint(update_course_app)
course_app.register_blueprint(get_course_app)
