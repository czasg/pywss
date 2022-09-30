# coding: utf-8
from urllib.parse import unquote


def parse_cookies(headers):
    cookies = {}
    for value in headers.get("Cookie", "").split(";"):
        values = value.strip().split("=", 1)
        if len(values) != 2:
            continue
        cookies[values[0]] = values[1]
    return cookies


def parse_params(path):
    params = {}
    paths = path.split("?", 1)
    if len(paths) != 2:
        return params
    for p in paths[1].split("&"):
        ps = p.split("=", 1)
        if len(ps) != 2:
            continue
        k, v = ps
        if k not in params:
            params[k] = v
        elif isinstance(params[k], list):
            params[k].append(v)
        else:
            params[k] = [params[k], v]
    return params


def parse_request_line(fp):
    line = fp.readline(65537)
    if len(line) > 65536:
        return "", "", "", "uri is too long"
    lines = str(line, 'iso-8859-1').rstrip("\r\n").split(maxsplit=2)
    if len(lines) != 3:
        return "", "", "", f"bad request line {line}"
    method, path, version = lines
    return method, unquote(path), version, None


def parse_headers(fp):
    headers = {}
    while True:
        line = fp.readline(65537)
        if len(line) > 65536:
            return headers, "headers is too long"
        if line in (b'\r\n', b'\n', b''):
            break
        lines = str(line, 'iso-8859-1').rstrip("\r\n").split(":", maxsplit=1)
        if len(lines) != 2:
            return headers, f"bad request header {line}"
        headers[lines[0].strip()] = lines[1].strip()
    return headers, None
