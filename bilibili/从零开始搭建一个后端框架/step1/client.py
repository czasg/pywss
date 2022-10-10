# coding: utf-8
import requests

print(requests.post("http://localhost:8080/hello", data="hello world").text)

""" curl
curl -X POST localhost:8080/hello -d "hello world"
"""
