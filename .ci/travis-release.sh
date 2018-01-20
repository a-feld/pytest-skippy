#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

set +u
# Check that a travis tag is set
# If it isn't set, exit immediately
[ -n "${TRAVIS_TAG}" ] || exit 0;
set -u

# Install twine prior to deployment
pip install twine

# Create source and wheel distributions
python setup.py sdist bdist_wheel

# Publish distribution to pypi
twine upload -u pypibot98b19 dist/*.whl dist/*.tar.*
