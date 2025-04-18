import json
import bcrypt
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from jwcrypto import jwk


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
secret_key_path = os.path.join(BASE_DIR, "../secret/secret_key.txt")
rsa_private_key_path = os.path.join(BASE_DIR, "../secret/rsa_private_key.pem")
rsa_public_key_path = os.path.join(BASE_DIR, "../secret/rsa_public_key.json")

def get_secret_key() -> bytes:
    try:
        with open(secret_key_path, "r") as fileRead:
            content = fileRead.read()
            if content:
                return content.encode("utf-8")
    except Exception:
        secret_key = Fernet.generate_key().decode("utf-8")

        with open(secret_key_path, "w") as fileWrite:
            fileWrite.write(secret_key)

        return secret_key.encode("utf-8")

def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    with open(rsa_private_key_path, "wb") as pem_file:
        pem_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    public_key = private_key.public_key()
    public_key_jwk = jwk.JWK.from_pyca(public_key)

    with open(rsa_public_key_path, "w") as json_file:
        json.dump(json.loads(public_key_jwk.export_public()), json_file, indent=4)

def encrypt(original_string: str) -> bytes:
    try:
        key = get_secret_key()
        ciper = Fernet(key)
        return ciper._encrypt_from_parts(original_string.encode(), 0, key[:16])
    except Exception:
        return b""

def decrypt(encrypted_string:bytes) -> str:
    try:
        key = get_secret_key()
        ciper = Fernet(key)
        return ciper.decrypt(encrypted_string).decode()
    except Exception:
        return ""

def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password

def verify_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)
