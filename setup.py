# coding: utf-8
import os
import re
import codecs

from setuptools import setup, find_packages

"""pip install twine
1、python setup.py check
2、python setup.py sdist
3、twine upload dist/__packages__-__version__.tar.gz
"""

"""MANIFEST.in
- include file-pattern ...
- exclude file-pattern ...
- recursive-include dir-pattern file-pattern ...
- recursive-exclude dir-pattern file-pattern ...
- global-include file-or-dir-pattern ...
- global-exclude file-or-dir-pattern ...
- graft dir-pattern
- prune dir-pattern
"""


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
    description="This Is A Web/WebSocket Server By Python",
    long_description="see https://github.com/czasg/pywss",
    author='czasg',
    author_email='972542644@qq.com',
    url='https://github.com/czasg/pywss',
    packages=find_packages(exclude=("test",)),
    include_package_data=True,
    zip_safe=False,
    license="MIT",
    entry_points={
        'console_scripts': [
            'pywss = entrypoint:main',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=[
        "loggus>=0.1.1",
    ],
)
