from flask import Blueprint, request, jsonify, request
from model.user_to_permission import UserToPermission
from model.users import RoleType, User
from util.request import handle_access_token, validate_request, handle_error

update_user_app = Blueprint("update_user", __name__)

@update_user_app.route("/update/<string:user_id>", methods=["PUT"])
@handle_access_token
@validate_request(["username", "email"])
@handle_error
def update_user_by_id(user_id):
    user = request.user
    payload = request.get_json()

    if user.role not in [RoleType.SUPER_ADMIN, RoleType.ADMIN]:
        raise Exception(f"คุณไม่มีสิทธิ์ในการอัพเดท user กรุณาติดต่อผู้ดูแลระบบ")

    existing_user = User().filter(filters=[("id", "=", user_id)], limit=1)

    if not existing_user:
        raise Exception(f"ไม่พบ user id={user_id} ในระบบ")

    existing_user.update({
        "username": payload["username"],
        "email": payload["email"],
        "role": payload.get("role", existing_user.role),
    })

    if payload.get("password", False):
        existing_user.change_password(payload["password"])

    permission_list = []
    if isinstance(payload.get("permissions", False), list):
        user_to_permission = UserToPermission().filter(filters=[("user_id", "=", user_id)], alway_list=True)
        for up in user_to_permission:
            up.unlink()

        for permission in payload["permissions"]:
            create_permission = UserToPermission().create({
                "permission_id": permission,
                "user_id": user.id,
            })
            permission_list.append(create_permission.permission_id)
    else:
        user_to_permission = UserToPermission().filter(filters=[("user_id", "=", user_id)], alway_list=True)
        permission_list = [up.permission_id for up in user_to_permission]

    user_updated = User().filter(filters=[("id", "=", user_id)], limit=1)

    return jsonify({
        "user_id": user_updated.id,
        "email": user_updated.email,
        "username": user_updated.username,
        "role": str(user_updated.role.name),
        "image_url": user_updated.image_url or "",
        "permissions": permission_list
    })