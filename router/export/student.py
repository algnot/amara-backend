import csv
from flask import Blueprint, Response
from io import StringIO
from model.student import Student
from util.request import handle_error, handle_access_token

export_student_app = Blueprint("export_student", __name__)

@export_student_app.route("/student", methods=["GET"])
@handle_access_token()
@handle_error
def export_student():
    all_students = Student().filter()

    if not isinstance(all_students, list):
        all_students = [all_students]

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["student_id", "รหัสนักเรียน", "ชื่อ (ไทย)", "นามสกุล (ไทย)", "ชื่อ (อังกฤษ)", "นามสกุล (อังกฤษ)", "sale_person_id"])

    for student in all_students:
        writer.writerow([student.id, student.student_id, student.firstname_th, student.lastname_th,
                         student.firstname_en, student.lastname_en, student.sale_person_id])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=students.csv"},
    )
