"""A pytest plugin to skip unchanged tests.
"""

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

test_requirements = ['tox']
dev_requirements = test_requirements + [
        'pytest',
        'pytest-git',
        'flake8',
        'coverage',
        'gitpython',
        'bumpversion',
        'sphinx',
        'sphinx_rtd_theme',
]


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ["-v", "-epy"]
        self.test_suite = True

    def run_tests(self):
        import tox
        tox.cmdline(self.test_args)


setup(
    name='pytest-autoskip',
    setup_requires=['setuptools_scm'],
    use_scm_version={'write_to': 'autoskip/_version.py'},
    description="Automatically skip tests that don't need to run!",
    long_description=long_description,
    license='MIT',
    url='https://github.com/a-feld/pytest-autoskip',
    author='Allan Feldman',
    author_email='allan.d.feldman@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Framework :: Pytest',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Environment :: Console',
    ],
    keywords='pytest incremental testing',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['pytest>=2.3.4', 'stdlib_list>=0.4.0'],
    tests_require=test_requirements,
    extras_require={
        'dev': dev_requirements,
    },
    entry_points={
        'pytest11': [
            'autoskip=autoskip.plugin',
        ],
    },
    cmdclass={'test': Tox},
)
