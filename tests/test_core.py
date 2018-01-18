import pytest
from autoskip.core import Autoskip


def fail_on_call(*args, **kwargs):
    assert False, "Called the fail_on_call test function"  # pragma: no cover


def module_to_file(d):
    def _module_to_file(module):
        return d.get(module, None)

    return _module_to_file


@pytest.fixture
def autoskip(request):
    _module_to_file = request.node.get_marker('module_to_file')
    if _module_to_file:
        _module_to_file = _module_to_file.args[0]
        if _module_to_file is False:
            _module_to_file = fail_on_call
        else:
            _module_to_file = module_to_file(_module_to_file)

    fake_traversal = request.node.get_marker('fake_traversal')
    if fake_traversal:
        traversal_values = fake_traversal.args[0]

        def _prepare_traversal(self, imported_filename):
            self.called = getattr(self, 'called', set())
            if imported_filename in self.called:
                assert False, ("traversal called "
                               "twice for same file")  # pragma: no cover

            self.called.add(imported_filename)
            return traversal_values[imported_filename]
    else:
        _prepare_traversal = Autoskip.prepare_traversal

    class _Autoskip(Autoskip):
        prepare_traversal = _prepare_traversal

        if _module_to_file:
            @staticmethod
            def convert_module_to_filename(module):
                return _module_to_file(module)

    changed_files = request.node.get_marker('changed_files')
    if changed_files is None:
        changed_files = set()
    else:
        changed_files = changed_files.args[0]

    safe_mode = request.node.get_marker('safe_mode')
    safe_mode = safe_mode or False

    autoskip = _Autoskip(changed_files, safe_mode=safe_mode)
    return autoskip


def test_module_in_should_run(autoskip):
    # set foo as a module to run
    autoskip.modules_to_run = {'foo'}

    # autoskip should run a module that's marked as needing a run
    assert autoskip.should_run('foo') is True
    assert 'foo' in autoskip.modules_to_run


@pytest.mark.module_to_file(False)
def test_ignored_module_is_not_traversed(autoskip):
    # os should be an ignored module in all cases
    # If any attempt to load the module is made, we should fail
    assert autoskip.should_run('os') is False


@pytest.mark.module_to_file({'foo': '/foo.py'})
@pytest.mark.changed_files({'/foo.py'})
def test_changed_file_causes_test_run(autoskip):
    # a module that maps to a changed file should cause a test run
    assert autoskip.should_run('foo') is True
    assert 'foo' in autoskip.modules_to_run


@pytest.mark.safe_mode
def test_missing_file_causes_run_in_safe_mode(autoskip):
    # Safe mode should force a test run when a module->file mapping cannot be
    # established
    assert autoskip.should_run('foo') is True
    assert 'foo' in autoskip.modules_to_run


@pytest.mark.parametrize('confirmed', [True, False])
def test_missing_module(confirmed, autoskip):
    if confirmed:
        # If we're not in safe mode, a missing module that's a confirmed module
        # should force a test run
        autoskip.confirmed_modules = {'foo'}
        assert autoskip.should_run('foo') is True
        assert 'foo' in autoskip.modules_to_run
    else:
        # If we're not in safe mode, a missing module that's not a confirmed
        # module shouldn't cause a test run
        assert autoskip.should_run('foo') is False


@pytest.mark.fake_traversal({'/foo.py': {'foo'}})
def test_circular_import(autoskip):
    assert autoskip.should_run('foo') is False


@pytest.mark.module_to_file({'foo': '/foo.py', 'bar': '/bar.py'})
@pytest.mark.changed_files({'/bar.py'})
@pytest.mark.fake_traversal({'/foo.py': {'bar'}})  # foo imports bar
def test_submodule_causes_run(autoskip):
    # since bar.py is changed and in the import tree, the test should run
    assert autoskip.should_run('foo') is True

    # Both foo and bar should be in modules_to_run now
    assert autoskip.modules_to_run == {'foo', 'bar'}


def test_prepare_traversal_updates_confirmed_modules(autoskip):
    assert len(autoskip.confirmed_modules) == 0

    import os
    _file = os.__file__
    # use only the raw python file
    if _file.endswith('.pyc'):
        _file = _file[:-1]
    autoskip.prepare_traversal(_file)

    # There has to be at least 1 confirmed module in there...
    assert len(autoskip.confirmed_modules) > 0


#  test modules_to_run is updated by complex graph traversal
#       i.e.     A
#               /  \
#              B    D
#               \  / \
#                C    E
#   if C is run, then B, D, A also cause a run
#   if B is run, only A should also cause a run
#   if D is run, only A should also cause a run
#   if E is run, D, A also cause a run

@pytest.mark.module_to_file(
    {'A': 'a.py',
     'B': 'b.py',
     'C': 'c.py',
     'D': 'd.py',
     'E': 'e.py'})
@pytest.mark.fake_traversal(
    {'a.py': {'B', 'D'},
     'b.py': {'C'},
     'c.py': set(),
     'd.py': {'C', 'E'},
     'e.py': set()})
@pytest.mark.parametrize('changed_file,modules_to_run', [
    ('a.py', {'A'}),
    ('b.py', {'A', 'B'}),
    ('c.py', {'A', 'B', 'C', 'D'}),
    ('d.py', {'A', 'D'}),
    ('e.py', {'A', 'D', 'E'}),
])
def test_traversal_logic(changed_file, modules_to_run, autoskip):
    autoskip.changed_files = {changed_file}
    assert autoskip.should_run('A') is True
    assert autoskip.modules_to_run == modules_to_run
