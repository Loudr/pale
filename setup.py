from setuptools import setup, find_packages
from os import path

with open(path.join(path.dirname(__file__), 'README.md')) as readme:
    long_description = readme.read()

setup(
    name="Pale",
    version="0.4.0",
    author="R. Kevin Nelson",
    author_email="kevin@rkn.la",
    description="Pale is a framework for crafting HTTP APIs.",
    license="Copyright 2015-present, Loudr.fm. All rights reserved.",
    url="https://github.com/Loudr/pale",
    packages=find_packages(),
    scripts=['bin/paledoc'],
    entry_points={
        'console_scripts': ['paledoc = pale.doc:run_pale_doc']
    }
)
