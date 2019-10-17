import os
import re
import codecs

from setuptools import setup, find_packages


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, *parts), 'r', encoding='utf-8').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name='pywss',
    version=find_version('pywss', '__init__.py'),
    description="This is a web-socket-server by python",
    long_description="see https://github.com/CzaOrz/Pywss",
    author='czaOrz',
    author_email='chenziangsg@163.com',
    url='https://github.com/CzaOrz/Pywss',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
