import datetime
import enum
import uuid
import json
import os
from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, Boolean, Enum, String
from sqlalchemy.orm import relationship
from model.base import Base
from util.encryptor import generate_rsa_keys
from jwcrypto import jwt, jwk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
secret_key_path = os.path.join(BASE_DIR, "../secret/secret_key.txt")
rsa_private_key_path = os.path.join(BASE_DIR, "../secret/rsa_private_key.pem")
rsa_public_key_path = os.path.join(BASE_DIR, "../secret/rsa_public_key.json")

class TokenType(enum.Enum):
    ACCESS = 1
    REFRESH = 2
    RESET_PASSWORD = 3

def default_expiration_time():
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=7)

class UserTokens(Base):
    __tablename__ = "user_tokens"

    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="tokens")

    type = Column(Enum(TokenType), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc), nullable=False)
    expires_at = Column(TIMESTAMP, default=default_expiration_time, nullable=False)
    revoked = Column(Boolean, default=False)

    def generate_token(self):
        return self.generate_refresh_token(), self.generate_access_token()

    def generate_jwt(self, expired_in, type: TokenType):
        payload = json.dumps({
            "sub": f"{self.user_id}:{self.id}",
            "type": str(type.value),
            "iat": int(self.created_at.timestamp()),
            "exp": int((datetime.datetime.now(datetime.timezone.utc) + expired_in).timestamp()),
        })

        key = self._load_signing_key()
        token = jwt.JWT(header={"alg": "RS256"}, claims=payload)
        token.make_signed_token(key)
        return token.serialize()

    def verify_token(self, token):
        key = self._load_verifying_key()
        decoded = jwt.JWT(key=key, jwt=token)
        payload = json.loads(decoded.claims)

        current_time = datetime.datetime.now(datetime.timezone.utc)
        expiration_time = datetime.datetime.fromtimestamp(payload["exp"], datetime.timezone.utc)
        if expiration_time < current_time:
            raise Exception("Token has expired")

        sub_value = payload.get("sub", "")
        if ":" not in sub_value:
            raise Exception("Invalid sub format")

        user_id, token_id = sub_value.split(":")
        token_data = self.get_by_id(token_id)
        if token_data.revoked:
            raise Exception("Token has been revoked")

        return payload

    def _load_signing_key(self):
        try:
            with open(rsa_private_key_path, "rb") as fh:
                return jwk.JWK.from_pem(fh.read())
        except FileNotFoundError:
            generate_rsa_keys()
            return self._load_signing_key()

    def _load_verifying_key(self):
        with open(rsa_public_key_path, "r") as fh:
            return jwk.JWK.from_json(fh.read())

    def generate_refresh_token(self):
        expired_in = datetime.timedelta(days=14)
        refresh_token = UserTokens()
        refresh_token.create({
            "user_id": self.user_id,
            "expires_at": datetime.datetime.now(datetime.timezone.utc) + expired_in,
            "type": TokenType.REFRESH
        })
        return refresh_token.generate_jwt(expired_in=expired_in, type=TokenType.REFRESH)

    def generate_access_token(self):
        expired_in = datetime.timedelta(hours=3)
        access_token = UserTokens()
        access_token.create({
            "user_id": self.user_id,
            "expires_at": datetime.datetime.now(datetime.timezone.utc) + expired_in,
            "type": TokenType.ACCESS
        })
        return access_token.generate_jwt(expired_in, type=TokenType.ACCESS)

    def generate_reset_password_token(self, user_id):
        expired_in = datetime.timedelta(minutes=15)
        access_token = UserTokens()
        access_token.create({
            "user_id": user_id,
            "expires_at": datetime.datetime.now(datetime.timezone.utc) + expired_in,
            "type": TokenType.RESET_PASSWORD
        })
        return access_token.generate_jwt(expired_in, type=TokenType.RESET_PASSWORD)
