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

* docs: 
* repository: 
