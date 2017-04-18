# encoding: utf-8

"""Python version cross-compatibility helpers.

These allow us to detect relevant differences for code generation, and overcome some of the minor alterations to
labels between Python 2 and 3 standard libraries.

The differences, in practice, are minor and are easily overcome through small blocks of version-dependant code. Even
built-in labels are not sacrosanct; they can be easily assigned to and imported.

A few common compatibility elements are required on a per-module basis, such as the use of the `__future__` import
illustrated below, careful use of object methods that are cross-compatible (such as avoiding `dict.iteritems`), and
conditional imports.
"""

from __future__ import unicode_literals

import sys


# Shortcuts for easier comparison elsewhere.
pypy = hasattr(sys, 'pypy_version_info')
py2 = sys.version_info < (3, )
py3 = not py2


# Compatibility for unicode strings.
# The `bytes` builtin is supported in both 2.7 and 3 and does not require polyfill.
str = unicode if py2 else str
