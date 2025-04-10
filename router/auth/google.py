import firebase_admin
import os
from flask import Blueprint, jsonify, request
from model.users import User
from util.encryptor import encrypt
from util.request import handle_error, validate_request
from firebase_admin import credentials, auth

login_with_google_app = Blueprint("login_with_google", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
secret_key_path = os.path.join(BASE_DIR, "../../secret/firebase_service_account_key.json")
cred = credentials.Certificate(secret_key_path)

firebase_admin.initialize_app(cred)

@login_with_google_app.route("/google", methods=["POST"])
@validate_request(["token"])
@handle_error
def login_with_google():
    payload = request.get_json()
    id_token = payload.get("token")

    decoded_token = auth.verify_id_token(id_token)
    uid = decoded_token["uid"]
    email = decoded_token.get("email")

    find_user = User().filter(filters=[("email", "=", encrypt(email))], limit=1)

    if not find_user:
        raise Exception(f"ผู้ใช้ {email} ยังไม่มีสิทธิ์ใช้งานระบบ กรุณาติดต่อผู้ดูแลระบบ")

    if find_user.google_uid == "":
        find_user = find_user.update({
            "google_uid": uid
        })

    elif find_user.google_uid != uid:
        raise Exception(f"ผู้ใช้ {email} ไม่สามารถเข้าสู่ระบบได้เนื่องจากบัญชีไม่ตรงกันกรุณาติดต่อผู้ดูแลระบบ")

    refresh_token, access_token = find_user.generate_token()

    return jsonify({
        "user_id": find_user.id,
        "email": find_user.email,
        "username": find_user.username,
        "role": str(find_user.role.name),
        "image_url": find_user.image_url or "",
        "refresh_token": refresh_token,
        "access_token": access_token,
    })