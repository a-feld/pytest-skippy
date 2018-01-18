import pytest

from autoskip.git import detect_changed_files


@pytest.fixture()
def test_repo(git_repo):
    path = git_repo.workspace

    commits = []
    for _ in range(3):
        hello_file = path / ('hello_%d.txt' % _)
        hello_file.write_text('hello world!')
        git_repo.run('git add hello_%d.txt' % _)
        git_repo.api.index.commit(str(_))

        # Record the root commit
        commits.append(git_repo.api.head.commit)

    return git_repo, commits


@pytest.mark.parametrize('target_branch,base_branch,expected', [
    (0, 'HEAD', set(['hello_1.txt', 'hello_2.txt'])),
    (0, 'HEAD~1', set(['hello_1.txt'])),
    (-1, 'HEAD', set()),
])
def test_git_changes(test_repo, target_branch, base_branch, expected):
    git_repo, commits = test_repo
    path = git_repo.workspace

    # Detect which files have changed relative to the root commit
    changed_files = detect_changed_files(
            commits[target_branch].hexsha,
            base_branch=base_branch, git_repo_dir=path)

    # Verify that the changed files are 'hello.txt'
    assert changed_files == expected
