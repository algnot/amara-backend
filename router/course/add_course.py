from flask import Blueprint, jsonify, request

from model.course import Course
from util.request import handle_error, validate_request

add_course_app = Blueprint("add_course", __name__)

@add_course_app.route("/new", methods=["POST"])
@validate_request(["course_code", "name_th", "name_en"])
@handle_error
def add_course():
    payload = request.get_json()

    existing_course = Course().filter(filters=[("course_code", "=", payload["course_code"])], limit=1)
    if existing_course:
        raise Exception(f"หลักสูตรรหัสวิชา {payload['course_code']} มีอยู่แล้วในระบบ ({existing_course.name_th})")

    course = Course().create({
        "course_code": payload["course_code"],
        "name_th": payload["name_th"],
        "name_en": payload["name_en"]
    })

    return jsonify({
        "id": course.id,
        "course_code": course.course_code,
        "name_th": course.name_th,
        "name_en": course.name_en
    })