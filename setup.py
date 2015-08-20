from setuptools import setup, find_packages
from os import path

from pale import __version__ as pale_version


with open(path.join(path.dirname(__file__), 'README.md')) as readme:
    long_description = readme.read()

setup(
    name="Pale",
    version=pale_version,
    author="R. Kevin Nelson",
    author_email="kevin@rkn.la",
    description="Pale is a framework for crafting HTTP APIs.",
    license="MIT License",
    url="https://github.com/Loudr/pale",
    packages=find_packages(exclude=('tests',)),
    scripts=['bin/paledoc'],
    install_requires=[
        'arrow==0.6.0'
    ],
    entry_points={
        'console_scripts': ['paledoc = pale.doc:run_pale_doc']
    }
)
