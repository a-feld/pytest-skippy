.. _quickstart:

**********
Quickstart
**********

Requirements
#############

This package interacts with `GIT <https://git-scm.com/>`_ and assumes that your
code and tests both exist within the same git repository.

* GIT
* pytest>=2.3.4

Installation
############

.. code:: bash

    pip install pytest-skippy

Usage
#####


This command uses the default target branch of ``origin/master``. The target
branch is the branch that has been modified. Most users should not have to
change the target branch when getting started.

.. code:: bash

    py.test --skippy
