.. image:: https://img.shields.io/pypi/v/pytest-autoskip.svg
   :target: https://pypi.org/project/pytest-autoskip/
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

Most tests that are run on a pull request don't actually exercise the changes
that are made. By running all tests (even if those tests are not relevant), the
test suite takes longer to complete and more machines may be needed to
parallelize tests to cut down on test time.

*pytest-autoskip* detects which tests don't need to run by generating a
complete import graph for your tests. If nothing in the import graph has
changed (according to GIT), the test is skipped! This approach saves time
(getting you test results faster) and money (using less machines for parallel
builds)!

Installation
############

.. code:: bash

    pip install pytest-autoskip

Usage
######

Add the ``--autoskip`` option to your pytest command.

To specify a target branch, use the ``--autoskip-target-branch`` option.

Example::

    py.test --autoskip --autoskip-target-branch origin/master

* docs: https://pytest-autoskip.readthedocs.io
* repository: https://github.com/a-feld/pytest-autoskip
