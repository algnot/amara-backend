from flask import Blueprint, jsonify, request

from util.encryptor import decrypt
from util.request import handle_error, validate_request

decrypt_data_app = Blueprint("decrypt_data_app", __name__)

@decrypt_data_app.route("/decrypt", methods=["POST"])
@validate_request(["payload"])
@handle_error
def sign_up():
    payload = request.get_json()

    return jsonify({
        "output": decrypt(payload["payload"])
    })