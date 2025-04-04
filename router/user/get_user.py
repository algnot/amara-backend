from flask import Blueprint, jsonify, request

from model.user_to_permission import UserToPermission
from model.users import RoleType, User
from util.request import handle_error, handle_access_token
from model.permission import Permission

get_user_app = Blueprint("get_user", __name__)

@get_user_app.route("/get/<string:user_id>", methods=["GET"])
@handle_access_token
@handle_error
def get_user_by_id(user_id):
    user = request.user

    if user.role not in [RoleType.SUPER_ADMIN, RoleType.ADMIN]:
        raise Exception(f"คุณไม่มีสิทธิ์ในการเข้าถึงข้อมูล user กรุณาติดต่อผู้ดูแลระบบ")

    existing_user = User().filter(filters=[("id", "=", user_id)], limit=1)

    if not existing_user:
        raise Exception(f"ไม่พบ user id={user_id} ในระบบ")

    permission_list = []
    if existing_user.role in [RoleType.SUPER_ADMIN, RoleType.ADMIN]:
        all_permission = Permission().filter()
        for permission in all_permission:
            permission_list.append({
                "id": permission.id,
                "key": permission.key,
                "name": permission.name,
                "description": permission.description,
            })
    else:
        user_to_permission = UserToPermission().filter(filters=[("user_id", "=", user_id)], alway_list=True)
        permission_ids = [up.permission_id for up in user_to_permission]
        user_permission = Permission().filter([("id", "in", permission_ids)], alway_list=True)
        for permission in user_permission:
            permission_list.append({
                "id": permission.id,
                "key": permission.key,
                "name": permission.name,
                "description": permission.description,
            })

    return jsonify({
        "user_id": existing_user.id,
        "email": existing_user.email,
        "username": existing_user.username,
        "role": str(existing_user.role.name),
        "image_url": existing_user.image_url or "",
        "permissions": permission_list
    })