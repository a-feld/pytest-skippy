.. _userguide:

**********
User Guide
**********

Overview
#########

pytest-autoskip automatically skips tests that don't need to run!

The process for determining if a test needs to run involves

#. Generating a set of changed files by querying GIT
#. Generating an import graph for each test file using the python
   :py:mod:`ast` module and :py:mod:`pkgutil` importers/loaders.
#. If any files in the import graph have been modified, the test needs to run!


PyTest Command Line Options
############################

``--autoskip``
**************
(*Default*: ``False``)

Enables this plugin, automatically skipping tests when applicable.

``--autoskip-target-branch``
****************************
(*Default*: ``origin/master``)

The target branch is the branch that has been modified. This branch parameter
is passed to ``git merge-base`` to determine which files have been changed.

For example, for a pull request using github and Travis-CI, the target branch
is stored in an environment variable called ``TRAVIS_PULL_REQUEST_BRANCH``.

.. _safe-mode:

``--autoskip-safe``
*******************
(*Default*: ``False``)

Safe mode changes the behavior of the autoskip plugin so that any import that
cannot be resolved forces a test run.

This makes sure that if a module is missing for any reason the test that would
catch the missing import is run.

Using this mode is likely to result in many false positives, causing tests to
run when it may not be necessary.
