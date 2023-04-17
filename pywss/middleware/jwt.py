# coding: utf-8
import json
import time
import pywss
import base64
import hashlib

from pywss.constant import *


def NewJWTHandler(
        secret: str = "pywss",
        expire: int = 3600,
        ignore_route: tuple = (),
        ignore_startswith: tuple = (),
        ignore_endswith: tuple = (),
        ignore_method_route: tuple = (),
):
    jwt = JWT(secret, expire)

    def jwtHandler(ctx: pywss.Context):
        ctx.data.jwt = jwt
        if ignore_route and ctx.route in ignore_route:
            ctx.next()
            return
        if ignore_startswith and ctx.route.startswith(ignore_startswith):
            ctx.next()
            return
        if ignore_endswith and ctx.route.endswith(ignore_endswith):
            ctx.next()
            return
        for m, r in ignore_method_route:
            if m == ctx.method and ctx.route in r:
                ctx.next()
                return
        try:
            token = ctx.headers.get(HeaderAuthorization)
            ctx.data.jwt_payload = jwt.decrypt(token)
        except:
            ctx.set_status_code(StatusForbidden)
            return
        ctx.next()

    return jwtHandler


class JWT:

    def __init__(self, secret: str, expire: int = 3600):
        self.secret = secret.encode()
        self.expire = expire
        self.header = base64.b64encode(json.dumps({
            "alg": "HS256",
            "typ": "JWT",
        }, ensure_ascii=False).encode())

    def encrypt(self, **kwargs):
        kwargs.update(exp=int(time.time()) + self.expire)
        payload = base64.b64encode(json.dumps(kwargs, ensure_ascii=False).encode())

        sha256 = hashlib.sha256()
        sha256.update(self.header)
        sha256.update(payload)
        sha256.update(self.secret)
        signature = sha256.hexdigest()

        return f"{self.header.decode()}.{payload.decode()}.{signature}"

    def decrypt(self, token: str) -> dict:
        if token.startswith("Bearer"):
            token = token.replace("Bearer", "", 1).strip()

        tokens = token.split(".")
        if len(tokens) != 3:
            raise Exception("Invalid JWT Token")

        header, payload, signature = tokens  # type: str
        sha256 = hashlib.sha256()
        sha256.update(header.encode())
        sha256.update(payload.encode())
        sha256.update(self.secret)
        if sha256.hexdigest() != signature:
            raise Exception("Invalid JWT Token, Signature Except")

        jwt_payload = json.loads(base64.b64decode(payload))
        if jwt_payload.get("exp", 0) < int(time.time()):
            raise Exception("JWT Token Expire")

        return jwt_payload
