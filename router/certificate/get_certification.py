from flask import Blueprint, jsonify

from model.certificate import Certificate
from model.course import Course
from model.saleperson import SalePerson
from model.student import Student
from util.request import handle_error, handle_access_token

get_certification_app = Blueprint("get_certification", __name__)

@get_certification_app.route("/get/<string:certification_number>", methods=["GET"])
@handle_access_token
@handle_error
def get_certification(certification_number):
    certification = Certificate().filter(filters=[("certificate_number", "=", certification_number)], limit=1)

    if not certification:
        raise Exception("ไม่พบเลขที่ใบประกาศนี้ในระบบ")

    course = Course().filter(filters=[("id", "=", certification.course_id)], limit=1)
    if not course:
        raise Exception("ไม่พบคอร์สเรียนนี้ในระบบ")

    student = Student().filter(filters=[("id", "=", certification.student_id)], limit=1)
    if not student:
        raise Exception("ไม่พบข้อมูลนักเรียนดังกล่าวในระบบ")

    sale_person = SalePerson().filter(filters=[("id", "=", student.sale_person_id)], limit=1)
    sale_person_name = ""
    if sale_person:
        sale_person_name = sale_person.firstname + " " + sale_person.lastname

    return jsonify({
        "id": certification.id,
        "certificate_number": certification.certificate_number,
        "start_date": certification.start_date,
        "end_date": certification.end_date,
        "batch": certification.batch,
        "given_date": certification.given_date,
        "course": {
            "id": course.id,
            "course_code": course.course_code,
            "name_th": course.name_th,
            "name_en": course.name_en,
            "version": str(float(course.certificate_version)),
        },
        "student": {
            "id": student.id,
            "student_id": student.student_id,
            "firstname_th": student.firstname_th,
            "lastname_th": student.lastname_th,
            "firstname_en": student.firstname_en,
            "lastname_en": student.lastname_en,
            "sale_person": sale_person_name,
        }
    })

@get_certification_app.route("/get-certificate/<string:certification_number>", methods=["GET"])
@handle_error
def get_public_certification(certification_number):
    certification = Certificate().filter(filters=[("certificate_number", "=", certification_number)], limit=1)

    if not certification:
        raise Exception("ไม่พบเลขที่ใบประกาศนี้ในระบบ")

    course = Course().filter(filters=[("id", "=", certification.course_id)], limit=1)
    if not course:
        raise Exception("ไม่พบคอร์สเรียนนี้ในระบบ")

    student = Student().filter(filters=[("id", "=", certification.student_id)], limit=1)
    if not student:
        raise Exception("ไม่พบข้อมูลนักเรียนดังกล่าวในระบบ")

    def censor_name(name):
        if len(name) > 3:
            return name[0] +  name[1] + "***" + name[-1]

        if len(name) > 2:
            return name[0] + "***" + name[-1]

        return name

    return jsonify({
        "id": certification.id,
        "certificate_number": certification.certificate_number,
        "start_date": certification.start_date,
        "end_date": certification.end_date,
        "batch": certification.batch,
        "given_date": certification.given_date,
        "course": {
            "id": course.id,
            "course_code": course.course_code,
            "name_th": course.name_th,
            "name_en": course.name_en,
            "version": str(float(course.certificate_version)),
        },
        "student": {
            "id": student.id,
            "student_id": student.student_id,
            "firstname_th": student.firstname_th,
            "lastname_th": censor_name(student.lastname_th),
            "firstname_en": student.firstname_en,
            "lastname_en": censor_name(student.lastname_en),
        }
    })
