#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function

import os
import sys
import codecs


try:
	from setuptools.core import setup, find_packages
except ImportError:
	from setuptools import setup, find_packages


if sys.version_info < (2, 7):
	raise SystemExit("CPython 2.7, compatible, or newer runtime is required.")
elif sys.version_info > (3, 0) and sys.version_info < (3, 3):
	raise SystemExit("CPython 3.3, compatible, or newer runtime is required.")

version = description = url = author = author_email = ""  # Silence linter warnings.
exec(open(os.path.join("marrow", "dsl", "release.py")).read())  # Actually populate those values.

here = os.path.abspath(os.path.dirname(__file__))

tests_require = [
		'pytest',  # test collector and extensible runner
		'pytest-cov',  # coverage reporting
		'pytest-flakes',  # syntax validation
		'pytest-catchlog',  # log capture
		'pytest-isort',  # import ordering
	]


setup(
	name = "marrow.dsl",
	version = version,
	description = description,
	long_description = codecs.open(os.path.join(here, 'README.rst'), 'r', 'utf8').read(),
	url = url,
	download_url = 'https://github.com/marrow/dsl/releases',
	author = author.name,
	author_email = author.email,
	license = 'MIT',
	keywords = ['template', 'text processing', 'source translation', 'dsl', 'marrow', 'marrow.dsl'],
	classifiers = [
			"Development Status :: 5 - Production/Stable",
			"Intended Audience :: Developers",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
			"Programming Language :: Python :: 2",
			"Programming Language :: Python :: 2.7",
			"Programming Language :: Python :: 3",
			"Programming Language :: Python :: 3.3",
			"Programming Language :: Python :: 3.4",
			"Programming Language :: Python :: 3.5",
			"Programming Language :: Python :: 3.6",
			"Programming Language :: Python :: Implementation :: CPython",
			"Programming Language :: Python :: Implementation :: PyPy",
			"Programming Language :: Python",
			"Topic :: Software Development :: Libraries :: Python Modules",
			"Topic :: Software Development :: Libraries",
			"Topic :: Utilities",
		],
	
	packages = find_packages(exclude=['bench', 'docs', 'example', 'test', 'htmlcov']),
	include_package_data = True,
	package_data = {'': ['README.rst', 'LICENSE.txt']},
	zip_safe = True,
	
	namespace_packages = [
			'marrow',
			'marrow.dsl',
		],
	entry_points = {
			'marrow.dsl': []
		},
	
	setup_requires = [
			'pytest-runner',
		] if {'pytest', 'test', 'ptr'}.intersection(sys.argv) else [],
	install_requires = [],
	tests_require = tests_require,
	extras_require = {
			'development': tests_require + ['pre-commit'],  # Development requirements are the testing requirements.
		},
)
