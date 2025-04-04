from flask import Blueprint, jsonify, request

from model.certificate import Certificate
from model.course import Course
from util.request import handle_error, validate_request, handle_access_token

update_certificate_app = Blueprint("update_certificate", __name__)

@update_certificate_app.route("/update/<string:certificate_number>", methods=["PUT"])
@validate_request(["start_date", "end_date", "given_date", "batch"])
@handle_access_token()
@handle_error
def update_course(certificate_number):
    payload = request.get_json()

    existing_certificate = Certificate().filter(filters=[("certificate_number", "=", certificate_number)], limit=1)
    if not existing_certificate:
        raise Exception("ไม่พบใบประกาศนี้ในระบบ")

    updated_certificate = existing_certificate.update({
        "start_date": payload["start_date"],
        "end_date": payload["end_date"],
        "given_date": payload["given_date"],
        "batch": payload["batch"]
    })

    return jsonify({
        "id": updated_certificate.id,
        "certificate_number": updated_certificate.certificate_number,
        "start_date": updated_certificate.start_date,
        "end_date": updated_certificate.end_date,
        "batch": updated_certificate.batch,
        "given_date": updated_certificate.given_date,
        "course_id": updated_certificate.course_id,
        "student_id": updated_certificate.student_id
    })