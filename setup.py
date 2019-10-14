#!/usr/bin/env python
# coding:utf-8
from setuptools import setup, find_packages

setup(
    name='pywss',
    version='0.0.1',
    description="This is a web-socket-server by python",
    long_description="see https://github.com/CzaOrz/Pywss",
    author='czaOrz',
    author_email='chenziangsg@163.com',
    url='https://github.com/CzaOrz/Pywss',
    packages=find_packages('./pywss'),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
