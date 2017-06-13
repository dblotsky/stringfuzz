#!/usr/bin/env python3

import os

from setuptools import setup

setup(
    name         = 'stringfuzz',
    version      = '0.1',
    description  = 'Fuzzer for SMTLIB 2.x solvers.',
    author       = 'Dmitry Blotsky',
    author_email = 'dmitry.blotsky@gmail.com',
    url          = 'https://github.com/dblotsky/stringfuzz',
    scripts      = ['bin/stringfuzzx', 'bin/stringfuzzg', 'bin/stringstats'],
    packages     = ['stringfuzz'],
    package_dir  = {'stringfuzz': 'stringfuzz'},
)
