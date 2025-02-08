from flask import Blueprint, jsonify, request

from model.saleperson import SalePerson
from model.student import Student
from util.request import handle_error, validate_request

add_student_app = Blueprint("add_student", __name__)

@add_student_app.route("/new", methods=["POST"])
@validate_request(["firstname_th", "lastname_th", "firstname_en", "lastname_en", "ref_code"])
@handle_error
def add_student():
    payload = request.get_json()
    sale_person = SalePerson().filter(filters=[("reference_code", "=", payload["ref_code"])])

    if len(sale_person) == 0:
        raise Exception(f"ไม่พบรหัส CS นี้ในระบบ")

    sale_person = sale_person[0]

    student = Student().create({
        "firstname_th": payload["firstname_th"],
        "lastname_th": payload["lastname_th"],
        "firstname_en": payload["firstname_en"],
        "lastname_en": payload["lastname_en"],
        "sale_person_id": sale_person.id,
    })

    return jsonify({
        "firstname_th": student.firstname_th,
        "lastname_th": student.lastname_th,
        "firstname_en": student.firstname_en,
        "lastname_en": student.lastname_en,
        "student_id": student.student_id,
    })