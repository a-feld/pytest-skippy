import os
import subprocess


def detect_changed_files(target_branch, base_branch='HEAD', git_repo_dir=None):
    """Get a list of changed files in a git repo

    :param target_branch: The merge target for a branch.
    :type target_branch: str
    :param base_branch: The branch that's being merged (default: 'HEAD')
    :type base_branch: str
    :param git_repo_dir: The base directory of the git repository.
                         None = current directory. (Default)
    :type git_repo_dir: None or str

    :returns: A set of files that have changed in the git repository.
    :rtype: set
    """
    start_dir = os.getcwd()
    git_repo_dir = git_repo_dir or start_dir

    os.chdir(git_repo_dir)
    try:
        # Extract the SHA of the merge base
        target_sha = subprocess.check_output(
                ['git', 'merge-base', target_branch, base_branch],
                stderr=subprocess.STDOUT)
        if type(target_sha) is not str:
            target_sha = target_sha.decode('utf-8')

        # Remove the trailing newline
        target_sha = target_sha.strip()

        # Extract the changed files going into the merge
        changed_files = subprocess.check_output(
                ['git', 'diff', '%s..%s' % (target_sha, base_branch),
                    '--name-only'],
                stderr=subprocess.STDOUT)
        if type(changed_files) is not str:
            changed_files = changed_files.decode('utf-8')

        # Split changed files into a list
        changed_files = changed_files.strip()
        if not changed_files:
            return set()

        changed_files = changed_files.split('\n')

        # Coerce to absolute path
        return set(changed_files)
    finally:
        os.chdir(start_dir)
