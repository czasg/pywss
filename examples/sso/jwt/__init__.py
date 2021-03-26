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


class JWT:

    def __init__(self, secret: str = str(uuid.uuid4())):
        self.header = {"alg": "HS256", "typ": "JWT"}
        self.headerBase64 = self.toBase64(self.header)
        self.secret = secret.encode()

    def toBase64(self, obj):
        return base64.b64encode(json.dumps(obj, ensure_ascii=False).encode()).decode()

    def fromBase64(self, obj):
        return json.loads(base64.b64decode(obj.encode()).decode())

    def create(self, uid, una):
        iat = time.time()
        payload = {
            "uid": uid,  # 用户ID
            "una": una,  # 用户Name
            "iat": iat,  # jwt签发时间
            "exp": iat + 1800,  # jwt过期时间
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
        now = time.time()
        if payload["iat"] > now:
            return None, False
        if payload["exp"] < now:
            return None, False
        return payload, True


jwt = JWT(secret)

if __name__ == '__main__':
    print(jwt.headerBase64)
    print(jwt.fromBase64(jwt.headerBase64))
    token = jwt.create(1, "cza")
    print(token)
    print(jwt.valid(f"{Bearer}{token}"))
