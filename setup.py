#!/usr/bin/env python3

import os

from setuptools import setup, find_packages

setup(
    name         = 'stringfuzz',
    version      = '0.1',
    description  = 'Fuzzer for SMTLIB 2.x solvers.',
    author       = 'Dmitry Blotsky, Federico Mora',
    author_email = 'dmitry.blotsky@gmail.com',
    url          = 'https://github.com/dblotsky/stringfuzz',
    scripts      = ['bin/stringfuzzx', 'bin/stringfuzzg', 'bin/stringstats', 'bin/stringmerge'],
    packages     = find_packages(),
    package_dir  = {'stringfuzz': 'stringfuzz'},
)
