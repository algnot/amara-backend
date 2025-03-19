from flask import Blueprint, jsonify

from model.certificate import Certificate
from util.request import handle_error

delete_certification_app = Blueprint("delete_certification", __name__)

@delete_certification_app.route("/delete/<string:certificate_number>", methods=["DELETE"])
@handle_error
def get_certification(certificate_number):
    existing_certificate = Certificate().filter(filters=[("certificate_number", "=", certificate_number)], limit=1)
    if not existing_certificate:
        raise Exception("ไม่พบใบประกาศนี้ในระบบ")

    updated_certificate = existing_certificate.update({
        "archived": True
    })

    return jsonify({
        "id": updated_certificate.id,
        "certificate_number": updated_certificate.certificate_number,
        "start_date": updated_certificate.start_date,
        "end_date": updated_certificate.end_date,
        "batch": updated_certificate.batch,
        "given_date": updated_certificate.given_date
    })