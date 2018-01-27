import os
import pytest
import shutil
import tempfile as _tempfile
from pytest_skippy.parse import get_imported_modules


@pytest.fixture()
def tempfile():

    def write(value):
        if getattr(write, 'name', None):
            raise RuntimeError(
                    "Write called more than once")  # pragma: no cover

        with _tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(value)

        write.name = f.name

    yield write

    try:
        os.unlink(write.name)
    except AttributeError:  # pragma: no cover
        pass  # pragma: no cover


def test_basic_import_module(tempfile):
    """Tests basic usage of import statements

    Checks import of multiple modules in a single import statement.
    """
    tempfile(b'import foo, bar\nimport baz')
    modules, confirmed = get_imported_modules(tempfile.name)

    assert modules == {'foo', 'bar', 'baz'}
    assert confirmed == {'foo', 'bar', 'baz'}


def test_basic_from_import(tempfile):
    """Tests basic usage of from imports

    from imports should infer the right hand side of the import is
    potentially a module.

    Example:
    from foo import bar
    infers that there is potentially a foo.bar module
    """
    tempfile(b'from x import y, z\nfrom foo import bar')
    modules, confirmed = get_imported_modules(tempfile.name)

    assert modules == {'x', 'x.y', 'x.z', 'foo', 'foo.bar'}
    assert confirmed == {'x', 'foo'}


def test_imports_within_functions(tempfile):
    tempfile(b'''
def foo():
    import bar
    from baz import x
''')
    modules, confirmed = get_imported_modules(tempfile.name)

    assert modules == {'bar', 'baz', 'baz.x'}
    assert confirmed == {'bar', 'baz'}


def test_mix_of_confirmed_and_unconfirmed(tempfile):
    tempfile(b'''
def foo():
    import bar
    from baz import x, y
    import baz.x
''')
    modules, confirmed = get_imported_modules(tempfile.name)
    assert modules == {'bar', 'baz', 'baz.x', 'baz.y'}
    assert confirmed == {'bar', 'baz', 'baz.x'}


def test_imports_within_classes(tempfile):
    tempfile(b'''
class Foo(object):
    def bar():
        import baz

    def boo():
        from x import y
''')
    modules, confirmed = get_imported_modules(tempfile.name)

    assert modules == {'baz', 'x', 'x.y'}
    assert confirmed == {'baz', 'x'}


def test_syntax_error(tempfile):
    tempfile(b'''
import bar

def foo():
pass
''')
    with pytest.raises(SyntaxError):
        get_imported_modules(tempfile.name)


def test_relative_from_import(tempfile):
    tempfile(b'''
from .foo import bar

def foo():
    pass
''')
    modules, confirmed = get_imported_modules(tempfile.name)

    import os.path
    dirname, filename = os.path.split(tempfile.name)
    base_module = os.path.basename(dirname)
    derived_modules = ['.'.join((base_module, _)) for _ in ('foo', 'foo.bar')]
    expected = [base_module]
    expected.extend(derived_modules)

    expected_confirmed = {base_module, derived_modules[0]}
    expected_modules = set(expected)

    assert modules == expected_modules
    assert confirmed == expected_confirmed


def test_multilevel_relative_import(tempfile):
    tempfile(b'''


from ..foo import bar

def foo():
    pass
''')
    modules, confirmed = get_imported_modules(tempfile.name)

    import os.path
    base_dir, _ = os.path.split(os.path.split(tempfile.name)[0])
    base_module = os.path.basename(base_dir)

    expected_module = base_module+'.foo'
    candidate_module = expected_module+'.bar'

    expected_modules = {base_module, expected_module, candidate_module}
    expected_confirmed = {base_module, expected_module}

    assert modules == expected_modules
    assert confirmed == expected_confirmed


def test_relative_import_without_submodule(tempfile):
    tempfile(b'''

# comment for good measure
from . import foo
''')
    modules, confirmed = get_imported_modules(tempfile.name)
    import os.path
    dirname, filename = os.path.split(tempfile.name)
    base_module = os.path.basename(dirname)

    expected_modules = {base_module, base_module+'.foo'}
    expected_confirmed = {base_module}

    assert modules == expected_modules
    assert confirmed == expected_confirmed


def test_relative_import_converts_with_sys_path(monkeypatch):
    try:
        base_dir = _tempfile.mkdtemp()
        pkg_dir = _tempfile.mkdtemp(dir=str(base_dir))
        subpkg_dir = _tempfile.mkdtemp(dir=pkg_dir)
        with _tempfile.NamedTemporaryFile(delete=False, dir=subpkg_dir) as f:
            f.write(b'''
from . import bar
''')

        # Add the directory containing the directory to the sys.path
        import os.path
        monkeypatch.syspath_prepend(base_dir)

        pkg_name = os.path.basename(pkg_dir)
        subpkg_name = os.path.basename(subpkg_dir)

        # Get the imported modules
        modules, confirmed = get_imported_modules(f.name)
    finally:
        shutil.rmtree(base_dir)

    # Check that the absolute path contains the root package name
    expected_confirmed = {pkg_name, pkg_name+'.'+subpkg_name}
    assert confirmed == expected_confirmed
    assert modules == expected_confirmed | {pkg_name+'.'+subpkg_name+'.bar'}
