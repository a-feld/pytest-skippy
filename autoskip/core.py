from stdlib_list import stdlib_list

import autoskip.util as util
import autoskip.imp as imp
import autoskip.parse as parse

from collections import deque

IGNORED_MODULES = set(['pytest']) | set(stdlib_list())


class Autoskip(object):
    """Core implementation of autoskip logic

    This object maintains some amount of traversal state between
    :py:func:`should_run` calls in order to optimize control flow.

    :param changed_files: The files which should cause a test run (since
                          they've been edited)
    :type changed_files: set
    :param safe_mode: Runs a test whenever there's a module candidate that
                      cannot be imported. Only use this if your code uses
                      ``from module1 import module2`` syntax. This is not
                      necessary if your code only imports attributes with from
                      statements (example: ``from module import function``).
    :type safe_mode: bool
    """

    def __init__(self, changed_files, safe_mode=False):
        self.changed_files = changed_files
        self.safe_mode = safe_mode

        # intermediate state (used only at the end of a non-skipped traversal)
        self.import_tree = dict()

        # Non-safe mode state only
        # Can cause early skipping when a confirmed module fails to load
        self.confirmed_modules = set()

        # State controlling traversal
        # Any module in modules_to_run immediately returns True
        self.modules_to_run = set()

    def mark_as_run(self, imported_module):
        """Mark a module as causing a test run

        This also implicitly marks any modules that import the
        "imported_module" as needing to run.

        :param imported_module: The module that should cause a test run
        :type imported_module: str
        """
        flat_imports = util.flatten_imports(imported_module, self.import_tree)
        self.modules_to_run |= flat_imports

    def record_imports(self, module, submodules):
        """Updates the import graph

        Marks a set of submodules as being imported by a module.

        :param module: The module which imports the submodules
        :type module: str
        :param submodules: A group of modules which have been imported by the
                           module.
        :type submodules: set or list
        """
        for submodule in submodules:
            imported_by = self.import_tree.setdefault(submodule, set())
            imported_by.add(module)

    @staticmethod
    def convert_module_to_filename(module):
        """Converts a module name to a filename

        This method is mainly used for test method injection. It should not be
        called or overridden in normal use.

        :param module: A name of a module
        :type module: str

        :returns: A filename containing a definition for the module
        :rtype: str
        """
        return imp.convert_module_to_filename(module)

    def should_run(self, root_module):
        """Determine if a test should run for a given module

        This is the primary interface for autoskip. Autoskip will execute an
        import graph traversal and make a decision to run / skip the test. A
        test will be marked as needing to run if any of the files in the import
        graph have been modified.

        :param root_module: Generally, the module defining the test. This
                            module is the starting point for a traversal.
        :type root_module: str

        :returns: True if the test should run
        :rtype: bool
        """
        # Create an initial seed. The root module is always the start of the
        # traversal.
        imported_modules = deque((root_module,))

        # Create a record of traversed modules to prevent circular / re-entrant
        # traversal
        traversed = set()

        # The root module is not imported by anything initially
        self.import_tree.setdefault(root_module, set())

        # Submodules will be used to check for new modules causing run
        # (optimization to remove conversion of imported_modules to set which
        # can be an expensive operation)
        submodules = {root_module}

        while imported_modules:
            # Extract any modules which would force a run (by checking against
            # the cache). The deque->set conversion may be expensive so we use
            # the submodules value from the previous iteration instead.
            modules_causing_run = submodules & self.modules_to_run

            # Any modules which cause a run should also cause a run to occur in
            # the future. This updates the cache of the modules causing a run
            # so that a future traversal is short circuited.
            for imported_module in modules_causing_run:
                self.mark_as_run(imported_module)

            # If any imported module causes a run, then mark the test as
            # needing to run
            if modules_causing_run:
                return True

            # Pop imported module
            imported_module = imported_modules.popleft()

            # If the module is ignored, continue
            if imported_module in (IGNORED_MODULES | traversed):
                continue

            # Get filename
            imported_filename = self.convert_module_to_filename(
                    imported_module)

            # If we can't import something, we have to run the test if we're in
            # safe mode. Otherwise we might be able to ignore it.
            if not imported_filename:
                if self.safe_mode:
                    break
                # Some modules are definitely modules. (i.e. import pytest)
                # If they can't be imported, we must run the test
                elif imported_module in self.confirmed_modules:
                    break

                # Outside of safe mode - ignore the module if it's not
                # confirmed

                # This statement is not reached due to python's peephole code
                # optimizer. But we test for it.
                continue  # pragma: no cover

            # If file is in changed files, mark the test as needing to run.
            if imported_filename in self.changed_files:
                break

            # else, the file is not directly edited and we must traverse its
            # children

            submodules = self.prepare_traversal(imported_filename)

            # Update the import tree state with the discovered imports
            # The import tree maps {module: imported_by}
            self.record_imports(imported_module, submodules)

            # Add imported modules to traversal
            imported_modules.extend(submodules)

            # Mark this module as traversed to prevent import cycles
            traversed.add(imported_module)

        else:
            # If after the traversal no modules have been changed, the test can
            # be skipped
            assert len(imported_modules) == 0
            return False

        self.mark_as_run(imported_module)
        return True

    def prepare_traversal(self, imported_filename):
        """Extract submodules from a file

        This method also updates the state of the "confirmed_modules" attribute
        based on parsed statements that would cause be guaranteed to cause an
        ImportError if the module did not exist.

        :param imported_filename: Filename from which to parse import
                                  statements
        :type imported_filename: str

        :returns: A set of submodules imported in the file "imported_filename"
        :rtype: set
        """
        # Parse AST and return imported children. It's important to distinguish
        # between modules that are ambiguously of module type (as in the case
        # of from style imports) and module candidates that must be modules.
        #
        # Example:
        #   bar may be a module or an attribute of foo
        #   foo MUST be a module
        #
        #   from foo import bar
        submodules, confirmed_submodules = (
            parse.get_imported_modules(imported_filename))

        # Track confirmed, unambiguous imports for use outside of safe
        # mode
        self.confirmed_modules.update(confirmed_submodules)

        return submodules
