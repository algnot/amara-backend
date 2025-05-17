from functools import wraps

import sentry_sdk
from flask import request, jsonify

from model.system_config import SystemConfig
from model.user_to_permission import UserToPermission
from model.user_tokens import UserTokens, TokenType
from model.users import User, RoleType
from model.permission import Permission


def validate_request(required_fields):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            payload = request.get_json()

            missing_fields = []
            for field in required_fields:
                if field not in payload or payload[field] is None or payload[field] == "":
                    missing_fields.append(field)

            if missing_fields:
                return jsonify({
                    "status": False,
                    "message": f"กรุณาใส่ข้อมูลต่อไปนี้ {', '.join(missing_fields)}"
                }), 400
            return func(*args, **kwargs)
        return wrapper
    return decorator

def handle_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            maintenance_message = SystemConfig().filter(filters=[("key", "=", "maintenance_message")], limit=1)
            if maintenance_message:
                if maintenance_message.value != "":
                    return jsonify({
                        "status": False,
                        "message": maintenance_message.value
                    }), 400

            return func(*args, **kwargs)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            error_message = str(e)

            return jsonify({
                "status": False,
                "message": error_message
            }), 400
    return wrapper

def get_user_from_token(token: str, token_type=TokenType.ACCESS):
    payload = UserTokens().verify_token(token)

    if payload["type"] != str(token_type.value):
        raise ValueError("Invalid token")

    return payload

def handle_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"status": False, "message": "Authorization token missing"}), 403

        token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
        if not token:
            return jsonify({"status": False, "message": "Invalid token format"}), 403

        try:
            payload = UserTokens().verify_token(token)
            user = User().get_by_id(payload["sub"]["user_id"])
            sentry_sdk.set_user({
                "email": user.email,
                "name": user.username,
            })
            request.user = user
            request.token = payload
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return jsonify({"status": False, "message": str(e)}), 403

        return func(*args, **kwargs)

    return wrapper

def handle_access_token(permission=False):
    if permission is not None:
        permission = []

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return jsonify({"status": False, "message": "Authorization token missing"}), 403

            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
            if not token:
                return jsonify({"status": False, "message": "Invalid token format"}), 403

            try:
                user_data = get_user_from_token(token, TokenType.ACCESS)["sub"]
                user_id = int(user_data.split(":")[0])
                user = User().get_by_id(user_id)

                if user.role in [RoleType.SUPER_ADMIN, RoleType.ADMIN]:
                    user_permissions = Permission().filter(alway_list=True)
                    user_permissions = [up.key for up in user_permissions]
                else:
                    user_permissions = UserToPermission().filter(filters=[("user_id", "=", user_id)], alway_list=True)
                    user_permission_ids = [up.permission_id for up in user_permissions]
                    find_permission = Permission().filter(filters=[("id", "in", user_permission_ids)], alway_list=True)
                    user_permissions = [up.key for up in find_permission]

                request.user = user
                request.permissions = user_permissions

                if permission and user_permissions not in permission:
                    return jsonify({"status": False, "message": f"ผู้ใช้งานไม่มีสิทธิ์เข้าถึงกรุณาติดต่อผู้ดูแลระบบ ({', '.join(permission)})"}), 403

            except Exception as e:
                return jsonify({"status": False, "message": str(e)}), 403

            return func(*args, **kwargs)

        return wrapper
    return decorator

def handle_refresh_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"status": False, "message": "Authorization token missing"}), 403

        token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
        if not token:
            return jsonify({"status": False, "message": "Invalid token format"}), 403

        try:
            user_id = int(get_user_from_token(token, TokenType.REFRESH)["sub"].split(":")[0])
            user = User().get_by_id(int(user_id))
            request.user = user
        except Exception as e:
            return jsonify({"status": False, "message": str(e)}), 403

        return func(*args, **kwargs)

    return wrapper
