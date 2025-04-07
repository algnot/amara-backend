from flask import Blueprint, jsonify, request

from model.saleperson import SalePerson
from model.student import Student
from model.users import User
from util.request import handle_error, validate_request, handle_access_token

update_student_app = Blueprint("update_student", __name__)

@update_student_app.route("/update/<string:student_id>", methods=["PUT"])
@validate_request(["firstname_th", "lastname_th", "firstname_en", "lastname_en"])
@handle_access_token()
@handle_error
def update_student(student_id):
    payload = request.get_json()
    student = Student().filter(filters=[("student_id", "=", student_id)], limit=1)

    if not student:
        raise Exception("ไม่พบข้อมูลนักเรียนดังกล่าวในระบบ")

    if student.user_id != 0:
        user = User().filter(filters=[("id", "=", student.user_id)], limit=1)
        if user:
            user.update({
                "username": f"{payload['firstname_en']} {payload['lastname_en']}",
            })

    updated_student = student.update({
        "firstname_th": payload["firstname_th"],
        "lastname_th": payload["lastname_th"],
        "firstname_en": payload["firstname_en"],
        "lastname_en": payload["lastname_en"],
    })

    sale_person = SalePerson().filter(filters=[("id", "=", student.sale_person_id)], limit=1)
    sale_person_name = ""
    if sale_person:
        sale_person_name = sale_person.firstname + " " + sale_person.lastname

    return jsonify({
        "id": updated_student.id,
        "firstname_th": updated_student.firstname_th,
        "lastname_th": updated_student.lastname_th,
        "firstname_en": updated_student.firstname_en,
        "lastname_en": updated_student.lastname_en,
        "student_id": updated_student.student_id,
        "sale_person": sale_person_name,
    })