#!/usr/bin/env python

from setuptools import setup

__version__ = '0.1'

CLASSIFIERS = map(str.strip,
"""Development Status :: 4 - Beta
Environment :: Web Environment
Framework :: Bottle
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Natural Language :: English
Operating System :: POSIX :: Linux
Programming Language :: Python
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.7
Topic :: Internet :: WWW/HTTP :: WSGI
Topic :: Security
Topic :: Software Development :: Libraries :: Python Modules
""".splitlines())

setup(
    name="bottle-ldap",
    version=__version__,
    author="Stuart Jackson",
    author_email="zwgtdev@gmail.com",
    description="Authentication/Authorization library for Bottle using LDAP",
    license="MIT",
    long_description="bottleLdap is an LDAP Authentication/Authorization library"
        "for the Bottle web framework.",
    classifiers=CLASSIFIERS,
    install_requires=[
        'Bottle',
        'ldap'
    ],
    packages=['bottleLdap'],
    platforms=['Linux'],
)