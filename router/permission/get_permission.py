from flask import Blueprint, jsonify, request

from model.users import RoleType
from model.permission import Permission
from util.request import handle_error, handle_access_token

get_permission_app = Blueprint("get_permission", __name__)

@get_permission_app.route("/get/<string:permission_id>", methods=["GET"])
@handle_access_token()
@handle_error
def add_permission(permission_id):
    user = request.user

    if user.role not in [RoleType.SUPER_ADMIN]:
        raise Exception("user ของคุณไม่มีสิทธิ์สำหรับเพิ่ม permission")

    existing_permission = Permission().filter(filters=[("id", "=", permission_id)], limit=1)

    if not existing_permission:
        raise Exception(f"ไม่พบ permission id={permission_id}")

    return jsonify({
        "id": existing_permission.id,
        "key": existing_permission.key,
        "name": existing_permission.name,
        "description": existing_permission.description,
    })