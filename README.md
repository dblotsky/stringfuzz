Description
===========

A collection of tools to manipulate and generate SMT-LIB 2.x problems. There
are three main tools:

- `smtfuzzg` to generate new problems
- `smtfuzzx` to transform existing problems
- `smtstats` to measure properties of problems

Running
=======

Without installing, the scripts can be run from the repository root as follows:

    ./bin/smtfuzzg --help
    ./bin/smtfuzzx --help
    ./bin/smtstats --help

If installed, they can be run from anywhere as follows:

    smtfuzzg --help
    smtfuzzx --help
    smtstats --help

Installing
==========

    python3 setup.py install

Examples
========

To create a problem with concats nested 100 levels deep:

    ./bin/smtfuzzg concats --depth 100

To create the above problem and replace all characters with unprintable ones:

    ./bin/smtfuzzg concats --depth 100 | ./bin/smtfuzzx unprintable

To create and immediately feed a problem to Z3str3:

    ./bin/smtfuzzg concats --depth 100 | z3str3 -in
