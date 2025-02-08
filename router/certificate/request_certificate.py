from flask import Blueprint, jsonify, request

from model.certificate import Certificate
from util.request import handle_error, validate_request

request_certificate_app = Blueprint("request_certificate", __name__)

@request_certificate_app.route("/request", methods=["POST"])
@validate_request(["student_id", "course_id", "start_date", "end_date"])
@handle_error
def request_certificate():
    payload = request.get_json()

    existing_certificate = Certificate().filter(filters=[("student_id", "=", payload["student_id"]),
                                                         ("course_id", "=", payload["course_id"])])
    if existing_certificate:
        raise Exception("คุณได้ขอใบประกาศให้นักเรียนในหลักสูตรนี้แล้ว กรุณาลองเปลี่ยนหลักสูตรหรือติดต่อผู้ดูแลหากต้องการเปลี่ยนข้อมูลวันที่")

    created_certificate = Certificate().create({
        "certificate_number": "draft",
        "start_date": payload["start_date"],
        "end_date": payload["end_date"],
        "course_id": payload["course_id"],
        "student_id": payload["student_id"]
    })

    return jsonify({
        "id": created_certificate.id,
        "certificate_number": created_certificate.certificate_number,
        "start_date": created_certificate.start_date,
        "end_date": created_certificate.end_date,
        "batch": created_certificate.batch,
        "given_date": created_certificate.given_date,
        "course_id": created_certificate.course_id,
        "student_id": created_certificate.student_id
    })