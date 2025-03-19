from flask import Blueprint, jsonify
from model.course import Course
from util.request import handle_error

get_course_app = Blueprint("get_course", __name__)

@get_course_app.route("/get/<string:course_id>", methods=["GET"])
@handle_error
def update_course(course_id):
    existing_course = Course().filter(filters=[("id", "=", course_id)], limit=1)
    if not existing_course:
        raise Exception("ไม่พบหลักสูตรนี้ในระบบ")

    return jsonify({
        "id": existing_course.id,
        "course_code": existing_course.course_code,
        "name_th": existing_course.name_th,
        "name_en": existing_course.name_en,
        "version": str(existing_course.certificate_version),
    })