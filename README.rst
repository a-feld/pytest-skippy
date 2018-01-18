.. image:: https://readthedocs.org/projects/pytest-autoskip/badge/?version=latest
    :target: https://pytest-autoskip.readthedocs.io/en/latest/?badge=latest
.. image:: https://travis-ci.org/a-feld/pytest-autoskip.svg?branch=master
    :target: https://travis-ci.org/a-feld/pytest-autoskip
.. image:: https://codecov.io/gh/a-feld/pytest-autoskip/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/a-feld/pytest-autoskip

***************
PyTest Autoskip
***************

Automatically skip tests that don't need to run!

This library works with pytest to generate a complete import graph for your
tests. If nothing in the import graph has changed (according to GIT), the test
is skipped.

Usage
######

Add the ``--autoskip`` option to your pytest command.

To specify a target branch, use the ``--autoskip-target-branch`` option.

Example::

    py.test --autoskip --autoskip-target-branch origin/master

* docs: https://pytest-autoskip.readthedocs.io
* repository: https://github.com/a-feld/pytest-autoskip
