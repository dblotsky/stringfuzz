Description
===========

A collection of tools to manipulate and generate SMT-LIB 2.x problems. There
are three main tools:

- `stringfuzzg` to generate new problems
- `stringfuzzx` to transform existing problems
- `stringstats` to measure properties of problems

Installing
==========

    python3 setup.py install

Running
=======

Without installing, the scripts can be run from the repository root as follows:

    ./bin/stringfuzzg --help
    ./bin/stringfuzzx --help
    ./bin/stringstats --help

If installed, they can be run from anywhere as follows:

    stringfuzzg --help
    stringfuzzx --help
    stringstats --help

Examples
========

To create a problem with concats nested 100 levels deep:

    ./bin/stringfuzzg concats --depth 100

To create the above problem and replace all characters with unprintable ones:

    ./bin/stringfuzzg concats --depth 100 | ./bin/stringfuzzx unprintable

To create and immediately feed a problem to Z3str3:

    ./bin/stringfuzzg concats --depth 100 | z3str3 -in
