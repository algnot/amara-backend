from flask import Blueprint, jsonify, request

from model.activity_logs import ActivityLogs
from model.course import Course
from util.request import handle_error, validate_request, handle_access_token

update_course_app = Blueprint("update_course", __name__)

@update_course_app.route("/update/<string:course_id>", methods=["PUT"])
@validate_request(["course_code", "name_th", "name_en", "version"])
@handle_access_token()
@handle_error
def update_course(course_id):
    user_email = request.user.email
    payload = request.get_json()

    existing_course = Course().filter(filters=[("course_code", "=", payload["course_code"])], limit=1)
    if existing_course and existing_course.id != int(course_id):
        raise Exception(f"หลักสูตรรหัสวิชา {payload['course_code']} มีอยู่แล้วในระบบ ({existing_course.name_th})")

    course = Course().filter(filters=[("id", "=", course_id)], limit=1)
    if not course:
        raise Exception("ไม่พบหลักสูตรนี้ในระบบ")

    updated_course = course.update({
        "course_code": payload["course_code"],
        "name_th": payload["name_th"],
        "name_en": payload["name_en"],
        "certificate_version": int(payload["version"])
    })

    ActivityLogs().create_activity_log("course", course.id, f"""
    {user_email} ได้ทำการอัพเดทหลักสูตร
    <ul>
      <li>รหัสวิชา: <b>{updated_course.course_code}</b></li>
      <li>ชื่อหลักสูตร (ไทย): <b>{updated_course.name_th}</b></li>
      <li>ชื่อหลักสูตร (อังกฤษ): <b>{updated_course.name_en}</b></li>
      <li>Version ใบประกาศ: <b>{updated_course.certificate_version}</b></li>
    </ul>
    """)

    return jsonify({
        "id": updated_course.id,
        "course_code": updated_course.course_code,
        "name_th": updated_course.name_th,
        "name_en": updated_course.name_en,
        "version": str(updated_course.certificate_version),
    })