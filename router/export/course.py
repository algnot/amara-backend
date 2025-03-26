import csv
from flask import Blueprint, Response
from io import StringIO
from model.course import Course
from util.request import handle_error, handle_access_token

export_course_app = Blueprint("export_course", __name__)

@export_course_app.route("/course", methods=["GET"])
@handle_access_token
@handle_error
def export_course():
    all_course = Course().filter()

    if not isinstance(all_course, list):
        all_course = [all_course]

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["course_id", "รหัสวิชา", "ชื่อวิชา (ไทย)", "ชื่อวิชา (อังกฤษ)", "version เอกสาร"])

    for course in all_course:
        writer.writerow([course.id, course.course_code, course.name_th, course.name_en, course.certificate_version])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=students.csv"},
    )
