from flask import Blueprint, jsonify, request

from model.user_to_permission import UserToPermission
from model.users import RoleType, User
from util.encryptor import encrypt
from util.request import handle_error, handle_access_token, validate_request

create_user_app = Blueprint("create_user", __name__)

@create_user_app.route("/create", methods=["POST"])
@handle_access_token
@validate_request(["username", "email", "password", "role"])
@handle_error
def create_user():
    user = request.user
    payload = request.get_json()

    if user.role not in [RoleType.SUPER_ADMIN, RoleType.ADMIN]:
        raise Exception(f"คุณไม่มีสิทธิ์ในการสร้าง user กรุณาติดต่อผู้ดูแลระบบ")

    existing_user = User().filter(filters=[("email", "=", encrypt(payload["email"]))], limit=1)

    if existing_user:
        raise Exception(f"{payload['email']} มีอยู่แล้วในระบบ")

    user = User()
    user.username = payload["username"]
    user.email = payload["email"]
    user.role = payload["role"]
    user_created = user.sign_up(payload["password"])

    permission_list = []
    if isinstance(payload.get("permissions", False), list):
        for permission in payload["permissions"]:
            create_permission = UserToPermission().create({
                "permission_id": permission,
                "user_id": user.id,
            })
            permission_list.append(create_permission.permission_id)

    return jsonify({
        "user_id": user_created.id,
        "email": user_created.email,
        "username": user_created.username,
        "role": str(user_created.role.name),
        "image_url": user_created.image_url or "",
        "permissions": permission_list
    })