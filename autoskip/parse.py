import ast


class ImportVisitor(ast.NodeVisitor):
    """Record imported modules

    This NodeVisitor class recursively traverses an AST and records
    all modules that have been imported.
    """
    def __init__(self):
        super(ImportVisitor, self).__init__()
        self.imports = {}

    def visit_Import(self, node):
        for module in (_.name for _ in node.names):
            self.imports.setdefault(module, None)

    def visit_ImportFrom(self, node):
        # In "from foo import bar" type statements, bar may be a module or
        # simply an attribute of the module foo. Therefore, bar is referred to
        # as a candidate since the type of bar is ambiguous until runtime.
        candidates = self.imports.get(node.module, None)
        if not candidates:
            self.imports[node.module] = set()
            candidates = self.imports[node.module]

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
    >>> with tempfile.NamedTemporaryFile() as f:
    ...     x = f.write(b'''
    ... import os
    ...
    ... def inner():
    ...    import re
    ... ''')
    ...     f.file.flush()
    ...     modules, _ = get_imported_modules(f.name)
    ...     print(sorted([m for m in modules]))
    ['os', 're']


    :param filename: File path to a python file
    :type filename: str

    :returns: (modules, confirmed_modules)
    :rtype: tuple
    """
    with open(filename, 'r') as f:
        source = f.read()

    tree = ast.parse(source)

    visitor = ImportVisitor()

    imports = visitor.visit(tree)

    full_import_set = compress_imports(imports)
    confirmed_modules = set(imports.keys())

    return (full_import_set, confirmed_modules)
