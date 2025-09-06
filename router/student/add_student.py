from flask import Blueprint, jsonify, request

from model.activity_logs import ActivityLogs
from model.saleperson import SalePerson
from model.student import Student
from util.encryptor import encrypt
from util.request import handle_error, validate_request

add_student_app = Blueprint("add_student", __name__)

@add_student_app.route("/new", methods=["POST"])
@validate_request(["firstname_th", "lastname_th", "firstname_en", "lastname_en", "ref_code"])
@handle_error
def add_student():
    payload = request.get_json()
    sale_person = SalePerson().filter(filters=[("reference_code", "=", payload["ref_code"])])

    if not sale_person:
        raise Exception("ไม่พบรหัส CS นี้ในระบบ")

    existing_student = Student().filter(filters=[("firstname_th", "=", encrypt(payload[ "firstname_th"])),
                                                 ("lastname_th", "=", encrypt(payload[ "lastname_th"])), "or",
                                                 ("firstname_en", "=", encrypt(payload["firstname_en"])),
                                                 ("lastname_en", "=", encrypt(payload["lastname_en"]))], limit=1)

    if existing_student:
        raise Exception(f"ข้อมูลนักเรียน {payload['firstname_th']} {payload['lastname_th']} ({payload['firstname_en']} {payload['lastname_en']}) "
                        f"มีอยู่แล้วในระบบ รหัสนักเรียน {existing_student.student_id} ไม่สามารถสร้างซ้ำได้")

    student = Student().create({
        "firstname_th": payload["firstname_th"],
        "lastname_th": payload["lastname_th"],
        "firstname_en": payload["firstname_en"],
        "lastname_en": payload["lastname_en"],
        "sale_person_id": sale_person.id,
    })

    ActivityLogs().create_activity_log("student", student.id, f"""
        สร้างบัญชีนักเรียน {student.student_id}<br/>
        <ul>
          <li>ชื่อ (ไทย): <b>{student.firstname_th} {student.lastname_th}</b></li>
          <li>ชื่อ (อังกฤษ): <b>{student.firstname_en} {student.lastname_en}</b></li>
        </ul>
        """)

    return jsonify({
        "id": student.id,
        "firstname_th": student.firstname_th,
        "lastname_th": student.lastname_th,
        "firstname_en": student.firstname_en,
        "lastname_en": student.lastname_en,
        "student_id": student.student_id,
    })