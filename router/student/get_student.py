from flask import Blueprint, jsonify

from model.saleperson import SalePerson
from model.student import Student
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

    return jsonify({
        "student_id": student.student_id,
        "firstname_th": student.firstname_th,
        "lastname_th": student.lastname_th,
        "firstname_en": student.firstname_en,
        "lastname_en": student.lastname_en,
        "sale_person": sale_person_name,
    })
