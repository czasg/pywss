# coding: utf-8
import os
import json
import uuid
import time
import base64
import hashlib

secret = os.environ.get("JWT_SECRET", str(uuid.uuid4()))
Authorization = "Authorization"
Bearer = "Bearer "
PAYLOAD = "payload"


class JWT:

    def __init__(self, secret: str = str(uuid.uuid4())):
        self.header = {"alg": "HS256", "typ": "JWT"}
        self.headerBase64 = self.toBase64(self.header)
        self.secret = secret.encode()

    def toBase64(self, obj):
        return base64.b64encode(json.dumps(obj, ensure_ascii=False).encode()).decode()

    def fromBase64(self, obj):
        return json.loads(base64.b64decode(obj.encode()).decode())

    def exp(self, payload):
        return payload["exp"] < time.time()

    def iat(self, payload):
        return payload["iat"] > time.time()

    def rid(self, payload):
        return payload["rid"]

    def adm(self, payload):
        return self.rid(payload) == 0

    def uid(self, payload):
        return payload["uid"]

    def create(self, uid, una, rid):
        iat = time.time()
        payload = {
            "uid": uid,  # 用户ID
            "una": una,  # 用户Name
            "iat": iat,  # jwt签发时间
            "exp": iat + 1800,  # jwt过期时间
            "rid": rid,
        }
        payload = self.toBase64(payload)
        sha256 = hashlib.sha256(self.secret)
        sha256.update(f"{self.headerBase64}.{payload}".encode())
        return f"{self.headerBase64}.{payload}.{sha256.hexdigest()}"

    def valid(self, token: str):
        if not token.startswith(Bearer):
            return None, False
        tokens = token.replace(Bearer, "", 1).split(".")
        if len(tokens) != 3:
            return None, False
        headerBase64, payload, validSecret = tokens
        if self.headerBase64 != headerBase64:
            return None, False
        sha256 = hashlib.sha256(self.secret)
        sha256.update(f"{headerBase64}.{payload}".encode())
        if sha256.hexdigest() != validSecret:
            return None, False
        payload = self.fromBase64(payload)
        if self.iat(payload):
            return None, False
        if self.exp(payload):
            return None, False
        return payload, True


jwt = JWT(secret)
