from os.path import exists

from flask import Blueprint, request, jsonify

from model.saleperson import SalePerson
from util.request import handle_error, validate_request, handle_access_token

sale_person_app = Blueprint("sale_person", __name__, url_prefix="/sale-person")

@sale_person_app.route("/update/<string:sale_person_id>", methods=["PUT"])
@validate_request(["firstname", "lastname", "code"])
@handle_access_token()
@handle_error
def update_sale_person_by_id(sale_person_id):
    payload = request.get_json()
    sale_person = SalePerson().filter(filters=[("id", "=", sale_person_id)], limit=1)

    if not sale_person:
        raise Exception("ไม่พบผู้ขายนี้ในระบบ")

    existing_sale_person = SalePerson().filter(filters=[("reference_code", "=", payload["code"])], limit=1)
    if existing_sale_person and existing_sale_person.id != sale_person.id:
        raise Exception(f"มีผู้ขายที่ใช้รหัส {payload['code']} อยู่แล้ว")

    updated_sale_person = sale_person.update({
        "firstname": payload["firstname"],
        "lastname": payload["lastname"],
        "reference_code": payload["code"],
    })

    return jsonify({
        "id" : updated_sale_person.id,
        "firstname": updated_sale_person.firstname,
        "lastname": updated_sale_person.lastname,
        "reference_code": updated_sale_person.reference_code,
    })

@sale_person_app.route("/get/<string:sale_person_id>", methods=["GET"])
@handle_error
def get_sale_person_by_id(sale_person_id):
    sale_person = SalePerson().filter(filters=[("id", "=", sale_person_id)], limit=1)

    if not sale_person:
        raise Exception("ไม่พบผู้ขายนี้ในระบบ")

    return jsonify({
        "id" : sale_person.id,
        "firstname": sale_person.firstname,
        "lastname": sale_person.lastname,
        "reference_code": sale_person.reference_code,
    })

@sale_person_app.route("/new", methods=["POST"])
@validate_request(["firstname", "lastname", "code"])
@handle_error
def add_new_sale_person():
    payload = request.get_json()

    sale_person = SalePerson().filter(filters=[("reference_code", "=", payload["code"])], limit=1)

    if sale_person:
        raise Exception(f"ผู้ขายรหัส {payload['code']} มีอยู่ในระบบเรียบร้อยแล้ว")

    created_sale_person = SalePerson().create({
        "firstname": payload["firstname"],
        "lastname": payload["lastname"],
        "reference_code": payload["code"],
    })

    return jsonify({
        "id": created_sale_person.id,
        "code": created_sale_person.reference_code,
        "firstname": created_sale_person.firstname,
        "lastname": created_sale_person.lastname,
    })