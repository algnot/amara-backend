from flask import Blueprint, jsonify, request

from model.users import RoleType
from model.permission import Permission
from util.request import handle_error, handle_access_token, validate_request

update_permission_app = Blueprint("update_permission", __name__)

@update_permission_app.route("/update/<string:permission_id>", methods=["PUT"])
@handle_access_token()
@validate_request(["key", "name", "description"])
@handle_error
def update_permission_by_id(permission_id):
    payload = request.get_json()
    user = request.user

    if user.role not in [RoleType.SUPER_ADMIN]:
        raise Exception("user ของคุณไม่มีสิทธิ์สำหรับอัพเดท permission")

    existing_permission = Permission().filter(filters=[("id", "=", permission_id)], limit=1)

    if not existing_permission:
        raise Exception(f"ไม่พบ permission id={permission_id}")

    updated_permission = existing_permission.update({
        "key": payload["key"],
        "name": payload["name"],
        "description": payload["description"],
    })

    return jsonify({
        "id": updated_permission.id,
        "key": updated_permission.key,
        "name": updated_permission.name,
        "description": updated_permission.description,
    })