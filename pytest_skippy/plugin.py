import os.path
import pytest
import subprocess
import pytest_skippy.core as core
import pytest_skippy.git as git


def pytest_addoption(parser):
    parser.addoption("--skippy", action="store_true",
                     dest='skippy',
                     help="Skip unchanged tests (compared to git branch "
                          "target)")
    parser.addoption("--skippy-target-branch",
                     nargs='?',
                     default='origin/master',
                     dest='skippy_target_branch',
                     help="Target branch (merge target); used to extract a "
                          "list of changed files. (default: origin/master)")
    parser.addoption("--skippy-safe", action="store_true",
                     dest='skippy_safe',
                     help="When in safe mode, any modules that cannot be "
                          "imported force the test to run.")


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(session, config, items):
    """called after collection has been performed, may filter or re-order
    the items in-place.
    """
    if not (config.option.skippy and
            config.option.skippy_target_branch and
            items):
        return

    try:
        target_branch = config.option.skippy_target_branch
        changed_files = git.detect_changed_files(
                target_branch,
                git_repo_dir=str(session.fspath))
    except subprocess.CalledProcessError as e:
        config.warn('skippy-git',
                    'Call to git failed: %s' % str(e), fslocation=__file__)
        return

    changed_files = set([os.path.abspath(_) for _ in changed_files])

    # Instantiate the core skippy object.
    safe_mode = config.option.skippy_safe
    skippy = core.Skippy(changed_files, safe_mode=safe_mode)

    for item in items:
        # Any tests that don't have an analyzable module need to run
        if not hasattr(item, 'module'):
            continue

        item_module = item.module.__name__

        if not skippy.should_run(item_module):
            # Skip test
            item.add_marker(pytest.mark.skip)
