.. _limitations:

***********
Limitations
***********

Since this library does not actually import any code (due to potential side
effects of importing and performance), there are a number of limitations
surrounding the accuracy of this plugin.

Runtime changes to ``sys.path``
###############################

This library does not account for any changes to the python path at runtime.
Modifications to the python path at runtime may change which file is loaded by
an import statement.

If your code modifies ``sys.path`` at runtime, the use of :ref:`safe-mode` is
recommended.

Importing modules with ``from`` statements
###########################################

The type of literals that are imported with ``from`` style imports is ambiguous.

Consider the following statement::

    from foo import bar

In the statement above, is ``bar`` an attribute of ``foo`` or a module?

It's possible that ``foo.bar`` is a module and the type of ``bar`` will be a
module. In these cases, ``import foo.bar`` will succeed at runtime.

However, if ``bar`` is a function, ``import foo.bar`` will fail at runtime.
This plugin does not attempt to determine the type of ``bar``.

By default, pytest-autoskip assumes that if ``foo.bar`` cannot be located,
``bar`` must be an attribute of the module ``foo``. As a result, if ``bar`` is
in fact a missing module, the test will be skipped by default.

Therefore, if module imports with the ``from`` statement are expected,
:ref:`safe-mode` should be used.
