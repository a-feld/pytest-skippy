import tempfile
import autoskip.imp as imp


def test_bad_relative_import():
    result = imp.convert_module_to_filename('.asdf')
    assert result is None


def test_non_existent_module():
    result = imp.convert_module_to_filename('autoskip.dog.cat')
    assert result is None


def test_standard_module():
    result = imp.convert_module_to_filename('os')
    import os
    filename = os.__file__

    # Remove the "c" from the pyc
    if filename.endswith('.pyc'):
        filename = filename[:-1]

    assert result == os.path.realpath(filename)


def test_builtin_module():
    result = imp.convert_module_to_filename('sys')
    assert result is None


# This test verifies that the file is not actually imported. Only the loader is
# accessed to retrieve the filename.
def test_file_with_syntax_error():
    import os
    import sys
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
        f.write(b"World's best program")

    try:
        filename = os.path.realpath(f.name)
        d = os.path.dirname(f.name)
        sys.path.append(d)
        # remove .py
        mod_name = os.path.basename(filename)[:-3]
        result = imp.convert_module_to_filename(mod_name)

        assert result == filename
    finally:
        os.unlink(f.name)
