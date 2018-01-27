import ast
import os.path
import sys


class ImportVisitor(ast.NodeVisitor):
    """Record imported modules

    This NodeVisitor class recursively traverses an AST and records
    all modules that have been imported.
    """
    def __init__(self, filename):
        super(ImportVisitor, self).__init__()
        self.imports = {}

        # Store path to filename for deriving relative import paths
        self.directories, _ = os.path.split(os.path.abspath(filename))

    def visit_Import(self, node):
        for module in (_.name for _ in node.names):
            self.imports.setdefault(module, None)

    def visit_ImportFrom(self, node):

        module = node.module
        if node.level:
            # Handle relative imports
            path = self.directories
            for _ in range(node.level):
                path, prepend = os.path.split(path)

            # After resolving the base module, prepend it to the module name
            base_module = prepend

            # Attempt to resolve package relative to sys.path
            prepends = []
            while prepend:
                if path in sys.path:
                    break
                path, prepend = os.path.split(path)
                prepends.insert(0, prepend)
            else:
                # The module is not relative to anything in the sys.path
                prepends = []

            # Add the base module into the resolved module name
            prepends.append(base_module)

            # Build up each package path starting with the package root
            # Those modules are imported (detected as being within the sys.path
            # or assumed to be modules)
            for idx in range(1, len(prepends)+1):
                pkg_path = '.'.join(prepends[:idx])
                self.imports.setdefault(pkg_path, None)

            # This covers the
            # from . import foo
            # case
            if node.module is not None:
                prepends.append(node.module)

            module = '.'.join(prepends)

        # In "from foo import bar" type statements, bar may be a module or
        # simply an attribute of the module foo. Therefore, bar is referred to
        # as a candidate since the type of bar is ambiguous until runtime.
        candidates = self.imports.get(module, None)
        if not candidates:
            self.imports[module] = set()
            candidates = self.imports[module]

        for candidate in (_.name for _ in node.names):
            candidates.add(candidate)

    def visit(self, node):
        """Search AST for imported modules

        :returns: a dictionary of modules to submodule candidates
        :rtype: dict
        """
        super(ImportVisitor, self).visit(node)
        return self.imports


def compress_imports(imports):
    full_imports = set()
    for module, candidates in imports.items():
        full_imports.add(module)

        if candidates:
            for candidate in candidates:
                full_imports.add('.'.join((module, candidate)))

    return full_imports


def get_imported_modules(filename):
    """Return modules that are imported by a file

    This function will extract all modules that are imported within
    a python file. The return value includes imports that happen at
    scopes other than the top level scope.

    This parser does not execute any of the python code in the file.

    The parser will also return a set of confirmed modules (strings that are
    guaranteed to be interpreted as module types at runtime)

    ::

      from foo import bar  # foo is a confirmed module, bar is a candidate
      import bar  # bar is a confirmed module

    For example:

    >>> import tempfile
    >>> with tempfile.NamedTemporaryFile(delete=False) as f:
    ...     x = f.write(b'''
    ... import os
    ...
    ... def inner():
    ...    import re
    ... ''')
    >>> modules, _ = get_imported_modules(f.name)
    >>> print(sorted([m for m in modules]))
    ['os', 're']
    >>> import os ; os.unlink(f.name)


    :param filename: File path to a python file
    :type filename: str

    :returns: (modules, confirmed_modules)
    :rtype: tuple
    """
    with open(filename, 'r') as f:
        source = f.read()

    tree = ast.parse(source)

    visitor = ImportVisitor(filename)

    imports = visitor.visit(tree)

    full_import_set = compress_imports(imports)
    confirmed_modules = set(imports.keys())

    return (full_import_set, confirmed_modules)
