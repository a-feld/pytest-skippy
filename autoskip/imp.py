import os.path
import pkgutil


def convert_module_to_filename(module_name):
    """Find a module's file location

    Returns the canonical path to the file that defines a module. The canonical
    path is retrieved using a call to :py:func:`os.path.realpath`

    :param module_name: Full path to a module.
    :type module_name: str

    :returns: A string containing the filename of the requested
              module.

    :rtype: str

    Example:

    >>> import os.path
    >>> path = convert_module_to_filename('re')
    >>> os.path.split(path)[-1]
    're.py'
    """

    # If we can't import the module, return None
    try:
        for importer in pkgutil.iter_importers(module_name):
            if not importer:
                continue

            loader = importer.find_module(module_name)
            if loader and hasattr(loader, 'get_filename'):
                filename = loader.get_filename()
                if filename:
                    return os.path.realpath(filename)
    except ImportError:
        return
