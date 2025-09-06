from flask import Blueprint, jsonify, request

from model.activity_logs import ActivityLogs
from model.course import Course
from util.request import handle_error, validate_request, handle_access_token

add_course_app = Blueprint("add_course", __name__)

@add_course_app.route("/new", methods=["POST"])
@validate_request(["course_code", "name_th", "name_en"])
@handle_access_token()
@handle_error
def add_course():
    user_email = request.user.email
    payload = request.get_json()

    existing_course = Course().filter(filters=[("course_code", "=", payload["course_code"])], limit=1)
    if existing_course:
        raise Exception(f"หลักสูตรรหัสวิชา {payload['course_code']} มีอยู่แล้วในระบบ ({existing_course.name_th})")

    course = Course().create({
        "course_code": payload["course_code"],
        "name_th": payload["name_th"],
        "name_en": payload["name_en"],
        "certificate_version": int(payload["version"]),
    })

    ActivityLogs().create_activity_log("course", course.id, f"""
{user_email} ได้ทำการสร้างหลักสูตร
<ul>
  <li>รหัสวิชา: <b>{course.course_code}</b></li>
  <li>ชื่อหลักสูตร (ไทย): <b>{course.name_th}</b></li>
  <li>ชื่อหลักสูตร (อังกฤษ): <b>{course.name_en}</b></li>
  <li>Version ใบประกาศ: <b>{course.certificate_version}</b></li>
</ul>
""")

    return jsonify({
        "id": course.id,
        "course_code": course.course_code,
        "name_th": course.name_th,
        "name_en": course.name_en,
        "version": str(course.certificate_version),
    })