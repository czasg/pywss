# coding: utf-8
import time
import json
import base64
import hashlib


class JWT:

    def __init__(self, secret: str):
        self.headers = {
            "alg": "HS256",
            "typ": "JWT",
        }
        self.headers_b64 = base64.b64encode(json.dumps(self.headers).encode()).decode()
        self.secret = secret

    def verify(self, token: str) -> (dict, bool):
        h, p, s = token.split(".")
        headers: dict = json.loads(base64.b64decode(h.encode()).decode())
        payload: dict = json.loads(base64.b64decode(p.encode()).decode())

        if headers.get("alg") != "HS256":
            return payload, False,

        if payload.get("exp", 0) < time.time():
            return payload, False,

        sha256 = hashlib.sha256()
        sha256.update((h + p).encode())
        sha256.update(self.secret.encode())
        if sha256.hexdigest() != s:
            return payload, False,

        return payload, True

    def generate(self, username):
        payload = {
            "une": username,
            "exp": int(time.time()) + 60,
        }
        payload_b64 = base64.b64encode(json.dumps(payload).encode()).decode()

        sha256 = hashlib.sha256()
        sha256.update((self.headers_b64 + payload_b64).encode())
        sha256.update(self.secret.encode())
        sign = sha256.hexdigest()
        return f"{self.headers_b64}.{payload_b64}.{sign}"


client = JWT("sso")

if __name__ == '__main__':
    token = client.generate("sso")
    print(client.verify(token))
