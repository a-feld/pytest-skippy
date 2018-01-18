"""Integration Tests"""
import git


def test_plugin(testdir):
    repo = git.Repo.init(testdir.tmpdir)

    f_core = testdir.makepyfile(core="""
    def run():
        pass
    """)

    f_test = testdir.makepyfile("""
    from core import run

    def test_simple():
        run()
    """)

    repo.index.add([str(f_test), str(f_core)])
    repo.index.commit("Initial commit.")

    # Without any changes, the test should be skipped
    result = testdir.runpytest(
            "--autoskip", "--autoskip-target-branch", "master")
    result.assert_outcomes(skipped=1)

    # In safe mode, it should run since a from import is used to import the
    # function
    result = testdir.runpytest(
            "--autoskip",
            "--autoskip-target-branch", "master",
            "--autoskip-safe")
    result.assert_outcomes(passed=1)

    # Change an imported file
    f_core = testdir.makepyfile(core="""
    # Here's a comment I added
    def run():
        pass
    """)
    repo.git.checkout('HEAD', b="modify")
    repo.index.add([str(f_core)])
    repo.index.commit("Modify core.")

    # With changes, autoskip should run the test
    result = testdir.runpytest(
            "--autoskip",
            "--autoskip-target-branch", "master")
    result.assert_outcomes(passed=1)


def test_no_git_repo(testdir):
    testdir.makepyfile("""
    def test_simple():
        pass
    """)

    # Test will run by default if there's no git repo
    result = testdir.runpytest(
            "--autoskip",
            "--autoskip-target-branch", "master")
    result.assert_outcomes(passed=1)
