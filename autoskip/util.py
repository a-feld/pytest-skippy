from collections import deque


def flatten_imports(imported_module, import_tree):
    """Returns a set of all modules imported by imported_module

    The import tree is a :py:class:`dict` in the form
    {module: set(imported_by)}

    :param imported_module: A leaf module name
    :type imported_module: str
    :param import_tree: A dict in the form of {module: set(imported_by)}
    :type import_tree: str

    :returns: A set of modules that import imported_module
    :rtype: set

    Example:
    A is imported by B

    >>> flat = flatten_imports('A', {'A': {'B'}, 'B': set()})
    >>> sorted(list(flat))
    ['A', 'B']
    """
    flat_imports = {imported_module}

    # get all the modules that import "imported_module"
    to_traverse = deque(import_tree[imported_module])

    while to_traverse:
        module = to_traverse.popleft()

        # if we've already visited the node, continue
        if module in flat_imports:
            continue

        flat_imports.add(module)

        # add next traversal level
        to_traverse.extend(import_tree[module])

    return flat_imports
