from flask import Blueprint, jsonify, request

from model.users import RoleType
from model.permission import Permission
from util.request import handle_error, handle_access_token, validate_request

add_permission_app = Blueprint("add_permission", __name__)

@add_permission_app.route("/new", methods=["POST"])
@handle_access_token
@validate_request(["key", "name", "description"])
@handle_error
def add_permission():
    payload = request.get_json()
    user = request.user

    if user.role not in [RoleType.SUPER_ADMIN]:
        raise Exception("user ของคุณไม่มีสิทธิ์สำหรับเพิ่ม permission")

    existing_permission = Permission().filter(filters=[("key", "=", payload["key"])], limit=1)

    if existing_permission:
        raise Exception(f"permission {payload['key']} มีอยู่แล้วในระบบ")

    create_permission = Permission().create({
        "key": payload["key"],
        "name": payload["name"],
        "description": payload["description"],
    })

    return jsonify({
        "id": create_permission.id,
        "key": create_permission.key,
        "name": create_permission.name,
        "description": create_permission.description,
    })