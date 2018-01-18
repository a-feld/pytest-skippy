import pytest
import tempfile as _tempfile
from autoskip.parse import get_imported_modules


@pytest.fixture()
def tempfile():
    with _tempfile.NamedTemporaryFile() as f:
        def write(value):
            f.write(value)
            f.file.flush()
        write.name = f.name
        yield write


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
