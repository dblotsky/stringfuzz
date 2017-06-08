#!/usr/bin/env python3

import os

from setuptools import setup

setup(
    name         = 'smtfuzz',
    version      = '0.1',
    description  = 'Fuzzer for SMTLIB 2.0 solvers.',
    author       = 'Dmitry Blotsky',
    author_email = 'dmitry.blotsky@gmail.com',
    url          = 'https://github.com/dblotsky/thesis',
    scripts      = ['bin/smtfuzzx', 'bin/smtfuzzg', 'bin/smtstats'],
    packages     = ['smtfuzz'],
    package_dir  = {'smtfuzz': 'smtfuzz'},
)
