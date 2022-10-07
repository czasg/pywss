# coding: utf-8
import requests

requests.post("http://localhost:8080/test", data="test")

""" curl
curl -X POST localhost:8080/test -d test
"""
