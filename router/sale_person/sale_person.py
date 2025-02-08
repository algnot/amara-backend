from flask import Blueprint, request, jsonify

from model.saleperson import SalePerson
from util.request import handle_error, validate_request

sale_person_app = Blueprint("sale_person", __name__, url_prefix="/sale-person")

@sale_person_app.route("/new", methods=["POST"])
@validate_request(["firstname", "lastname", "code"])
@handle_error
def add_new_sale_person():
    payload = request.get_json()

    sale_person = SalePerson().filter(filters=[("reference_code", "=", payload["code"])], limit=1)

    if len(sale_person) > 0:
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