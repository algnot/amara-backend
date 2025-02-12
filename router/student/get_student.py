from flask import Blueprint, jsonify

from model.certificate import Certificate
from model.course import Course
from model.saleperson import SalePerson
from model.student import Student
from util.date import format_thai_date
from util.request import handle_error

get_student_app = Blueprint("get_student", __name__)

@get_student_app.route("/get/<string:student_id>", methods=["GET"])
@handle_error
def get_student_by_student_id(student_id):
    student = Student().filter(filters=[("student_id", "=", student_id)], limit=1)

    if not student:
        raise Exception("ไม่พบข้อมูลนักเรียนดังกล่าวในระบบ")

    sale_person = SalePerson().filter(filters=[("id", "=", student.sale_person_id)], limit=1)
    sale_person_name = ""
    if sale_person:
        sale_person_name = sale_person.firstname + " " + sale_person.lastname

    all_certificate = Certificate().filter(filters=[("student_id", "=", student.id), ("batch", "!=", "draft")])
    certificate_list = []

    if not isinstance(all_certificate, list):
        all_certificate = [all_certificate]

    for certificate in all_certificate:
        course = Course().filter(filters=[("id", "=", certificate.course_id)], limit=1)
        if not course:
            raise Exception("ไม่พบคอร์สเรียนนี้ในระบบ")

        certificate_list.append({
            "id": certificate.id,
            "certificate_number": certificate.certificate_number,
            "batch": certificate.batch,
            "course": {
                "id": course.id,
                "course_code": course.course_code,
                "name_th": course.name_th,
                "name_en": course.name_en,
            },
            "start_date": format_thai_date(certificate.start_date),
            "end_date": format_thai_date(certificate.end_date),
            "given_date": format_thai_date(certificate.given_date),
        })

    return jsonify({
        "id": student.id,
        "student_id": student.student_id,
        "firstname_th": student.firstname_th,
        "lastname_th": student.lastname_th,
        "firstname_en": student.firstname_en,
        "lastname_en": student.lastname_en,
        "sale_person": sale_person_name,
        "certificate": certificate_list,
    })
