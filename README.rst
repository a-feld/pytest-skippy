.. image:: https://img.shields.io/pypi/v/pytest-skippy.svg
   :target: https://pypi.org/project/pytest-skippy/
.. image:: https://readthedocs.org/projects/pytest-skippy/badge/?version=latest
    :target: https://pytest-skippy.readthedocs.io/en/latest/?badge=latest
.. image:: https://travis-ci.org/a-feld/pytest-skippy.svg?branch=master
    :target: https://travis-ci.org/a-feld/pytest-skippy
.. image:: https://ci.appveyor.com/api/projects/status/github/a-feld/pytest-skippy?svg=true
    :target: https://ci.appveyor.com/project/a-feld/pytest-skippy/branch/master
.. image:: https://codecov.io/gh/a-feld/pytest-skippy/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/a-feld/pytest-skippy

***************
pytest skippy
***************

Automatically skip tests that don't need to run!

Most tests that are run on a pull request don't actually exercise the changes
that are made. By running all tests (even if those tests are not relevant), the
test suite takes longer to complete and more machines may be needed to
parallelize tests to cut down on test time.

*pytest-skippy* detects which tests don't need to run by generating a
complete import graph for your tests. If nothing in the import graph has
changed (according to GIT), the test is skipped! This approach saves time
(getting you test results faster) and money (using less machines for parallel
builds)!

Installation
############

.. code:: bash

    pip install pytest-skippy

Usage
######

Add the ``--skippy`` option to your pytest command.

To specify a target branch, use the ``--skippy-target-branch`` option.

Example::

    py.test --skippy --skippy-target-branch origin/master

* docs: https://pytest-skippy.readthedocs.io
* repository: https://github.com/a-feld/pytest-skippy
