from flask import Blueprint, jsonify, request

from model.activity_logs import ActivityLogs
from model.user_to_permission import UserToPermission
from model.users import RoleType, User
from util.request import handle_access_token, validate_request, handle_error

update_user_app = Blueprint("update_user", __name__)


@update_user_app.route("/update/<string:user_id>", methods=["PUT"])
@handle_access_token()
@validate_request(["username", "email"])
@handle_error
def update_user_by_id(user_id):
    user = request.user
    payload = request.get_json()

    if user.role not in [RoleType.SUPER_ADMIN, RoleType.ADMIN]:
        raise Exception("คุณไม่มีสิทธิ์ในการอัพเดท user กรุณาติดต่อผู้ดูแลระบบ")

    existing_user = User().filter(filters=[("id", "=", user_id)], limit=1)

    if not existing_user:
        raise Exception(f"ไม่พบ user id={user_id} ในระบบ")

    prepare_update = {
        "username": payload["username"],
        "email": payload["email"],
    }

    if payload.get("role", "") != "":
        prepare_update["role"] = payload["role"]

    if payload["email"] != existing_user.email:
        prepare_update["google_uid"] = ""

    existing_user.update(prepare_update)

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
                "user_id": user_id,
            })
            permission_list.append(create_permission.permission_id)
    else:
        user_to_permission = UserToPermission().filter(filters=[("user_id", "=", user_id)], alway_list=True)
        permission_list = [up.permission_id for up in user_to_permission]

    user_updated = User().filter(filters=[("id", "=", user_id)], limit=1)

    ActivityLogs().create_activity_log("user", user_updated.id, f"""
    {user.email} ได้ทำการอัพเดทข้อมูลบัญชี <br/>
    <ul>
      <li>ชื่อผู้ใช้: <b>{user_updated.username}</b></li>
      <li>บทบาท: <b>{str(user_updated.role.name)}</b></li>
    </ul>
    """)

    return jsonify({
        "user_id": user_updated.id,
        "email": user_updated.email,
        "username": user_updated.username,
        "role": str(user_updated.role.name),
        "image_url": user_updated.image_url or "",
        "permissions": permission_list
    })