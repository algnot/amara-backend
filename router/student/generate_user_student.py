import random

from flask import Blueprint, jsonify
from model.student import Student
from model.users import User, RoleType
from util.request import handle_error, handle_access_token

generate_user_student_app = Blueprint("generate_user_student", __name__)

@generate_user_student_app.route("/generate-user/<string:student_id>", methods=["POST"])
@handle_access_token(permission=["modify-student-data"])
@handle_error
def generate_user_student(student_id):
    student = Student().filter(filters=[("student_id", "=", student_id)], limit=1)

    if not student:
        raise Exception("ไม่พบข้อมูลนักเรียนดังกล่าวในระบบ")

    random_password = str(random.randint(100000, 999999))

    if student.user_id == 0 or student.user_id is None:
        user = User()
        user.username = f"{student.firstname_en} {student.lastname_en}"
        user.email = student.student_id
        user.role = RoleType.STUDENT
        user = user.sign_up(random_password)
        student.update({
            "user_id": user.id,
        })
    else:
        user = User().filter(filters=[("id", "=", student.user_id)], limit=1)
        user.role = RoleType.STUDENT
        user.change_password(random_password)

    return jsonify({
        "login": user.email,
        "password": random_password
    })