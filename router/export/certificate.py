import csv
from flask import Blueprint, Response
from io import StringIO
from model.certificate import Certificate
from util.date import format_thai_date
from util.request import handle_error, handle_access_token

export_certificate_app = Blueprint("export_certificate", __name__)

@export_certificate_app.route("/certificate", methods=["GET"])
@handle_access_token
@handle_error
def export_certificate():
    all_certificate = Certificate().filter(filters=[("archived", "=", False)])

    if not isinstance(all_certificate, list):
        all_certificate = [all_certificate]

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["certificate_id", "เลขที่ใบประกาศ", "รุ่นที่", "วันที่เริ่มเรียน", "วันที่เรียนจบ", "วันที่มอบใบประกาศ", "student_id", "course_id"])

    for certificate in all_certificate:
        writer.writerow([certificate.id, certificate.certificate_number, certificate.batch, format_thai_date(certificate.start_date), format_thai_date(certificate.end_date),
                         format_thai_date(certificate.given_date), certificate.student_id, certificate.course_id])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=students.csv"},
    )
