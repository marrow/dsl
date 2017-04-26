==========
marrow.dsl
==========

    © 2011-2017 Alice Bevan-McGregor and contributors.

..

    https://github.com/marrow/dsl

..

    |latestversion| |ghtag| |downloads| |masterstatus| |mastercover| |masterreq| |ghwatch| |ghstar|


Contents
========

1. `What is this?`_

   1. `What's with the funny names?`_
   2. `Rationale and Goals`_

2. `Installation`_

   1. `Development Version`_

3. `Domain Specific Languages`_

   1. `Encoding Naming Scheme`_
   2. `Lines`_
   3. `Buffers`_
   4. `Context`_
   5. `Engine Metadata`_
   6. `Engine Customization`_
   7. `Transformation`_

      1. `Block Transformation`_
      2. `Inline Transformation`_
      3. `AST Transformation`_

5. `Version History`_
6. `License`_


What is this?
=============

Domain specific languages allow you to write code in ways more optimized to specialized tasks. These can often be
thought of as interpreters for programming languages other than the one the interpreter is written in, and you may
already be familiar with a few such as template engines, or testing frameworks. Marrow DSL is a framework for easily
constructing new ones in Python using a preprocessor methodology performing transformation seamlessly at module import
time.

Want to write a really fast template engine of your own? `You can do that. <https://github.com/marrow/cinje>`__

Want to write a testing framework for story driven development? `Totally possible. <https://gist.github.com/amcgregor/1338661>`__

Want to obfuscate or encrypt your code? We don't recommend it, but yeah, doable.

Want to prank your co-workers and turn their Python into Pascal or C? We beg you, please don't do this.


What's with the funny names?
----------------------------

You might notice the base name of the engine is ``GalfiDecoder`` – this was the original internal project name. Marrow
projects tend to follow a more... literal... naming scheme, but this legacy remains.  So what in the world is "galfi"?

It's a word from the constructed language `Lojban <http://www.lojban.org/>`_. A combination of Chinese "gǎi", English
"alter", Hindi "badalanā", Spanish "modificar", Russian "modificirovatʹ", and Arabic "gaiar". It translates as "(an
event) X modifies/alters/changes/transforms/converts Y into Z", and is a fairly literal interpretation for the
mechanism this DSL engine provides, where X is this package, Y is your DSL, and Z is Python code.

Specific engines, such as `cinje <https://github.com/marrow/cinje>`__ and korcu will be released using their literal
names, though. Lojban root words, or _gismu_ are neat: built from global natural languages, descriptive, and they
scratch the regular expression itch.


Rationale and Goals
-------------------

We find most DSLs (especially template engines) in Python to:

1. Be overly complex, often taking a classical lexer/parser/AST approach to language construction. This can be
   difficult for developers new to the language to understand or extend, and poses a hurdle to the understanding of
   the basic principles. Constructing new ways to write code should be easy, not hard.

2. Repeatedly solve the same problems in similar ways that could benefit from deduplication between engines. The needs
   of most engines are similar; these should be fulfilled by a common codebase benefitting many engines.

3. Duplicate functionality such as the import pipeline (e.g. to acquire an invokable object to generate templated
   text) or bytecode caching layer already present in Python, instead of leveraring these built-in tools.

Marrow DSL takes a simpler approach than most by:

1. Treating the domain-specific code fundamentally as lines of input _text_ which can trigger transformations,
   reducing lexing/parsing problems to simple string matching and manipulation. This results in a basic DSL framework
   less than a quarter the size of an average template engine, and engines utilizing Marrow DSL a fraction of that.

2. Ensuring transformation is seamless at module import time, allowing full utilization of Python's own internal
   bytecode cache as well as the existing package/module discovery and import mechanisms.

3. Allowing the bytecode resulting from translation (as managed by Python itself) to have no dependency at all on the
   engine that produced it, making the engine (and Marrow DSL) a build time, not production deployment dependency.

Domain-specific languages written using Marrow DSL integrate into general Python codebases seamlessly, and are
transformed in a predictable, understandable way that is easy to extend.


Installation
============

Installing ``marrow.dsl`` is easy, just execute the following in a terminal::

    pip install marrow.dsl

**Note:** We *strongly* recommend always using a container, virtualization, or sandboxing environment of some kind when
developing using Python; installing things system-wide is yucky (for a variety of reasons) nine times out of ten.  We
prefer light-weight `virtualenv <https://virtualenv.pypa.io/en/latest/virtualenv.html>`__, others prefer solutions as
robust as `Vagrant <http://www.vagrantup.com>`__.

If you add ``marrow.dsl`` to the ``install_requires`` argument of the call to ``setup()`` in your application's
``setup.py`` file, the engine will be automatically installed and made available when your own application or
library is installed. You can alternatively make ``marrow.dsl`` an installation-time dependency only by declaring it
against the ``setup_requires`` argument instead.

We recommend "less than" version number pinning to ensure there are no unintentional side-effects when updating.  Use
``marrow.dsl<1.1`` to get all bugfixes for the current release, and ``marrow.dsl<2.0`` to get bugfixes and feature
updates while ensuring that large breaking changes are not installed.


Development Version
-------------------

    |developstatus| |developcover| |ghsince| |issuecount| |ghfork|

Development takes place on `GitHub <https://github.com/>`__ in the
`marrow/dsl <https://github.com/marrow/dsl/>`__ project.  Issue tracking, documentation, and downloads
are provided there.

Installing the current development version requires `Git <http://git-scm.com/>`_, a distributed source code management
system.  If you have Git you can run the following to download and *link* the development version into your Python
runtime::

    git clone https://github.com/marrow/dsl.git
    (cd dsl; python setup.py develop)

You can then upgrade to the latest version at any time::

    (cd dsl; git pull; python setup.py develop)

If you would like to make changes and contribute them back to the project, fork the GitHub project, make your changes,
and submit a pull request.  This process is beyond the scope of this documentation; for more information see
`GitHub's documentation <http://help.github.com/>`_.


Domain Specific Languages
=========================

A Marrow DSL boils down to two things: DSL metadata registration and processing customization, represented as a class
registered via entry_points under the marrow.dsl namespace, and; one or more transformation classes registered under
the entry_points namespace for your named DSL which are used to inspect, claim, and transform lines of input.

The mechanism by which transformation is triggered may be somewhat alien: Python unicode decoding hooks for source
files, executed when opening the source file, prior to parsing, compilation, byte code storage, and evaluation during
import. To control this magic requires the internal use of Unicode encoding declaration and the ``# [en]coding:``
module encoding declaration to trigger transformation at import time.

Python modules written using a DSL are otherwise just ``.py`` files given a DSL encoding declaration.

In accordance with `PEP 3120 <https://www.python.org/dev/peps/pep-3120/>`__, the default encoding of the underlying
textual content of all pre-transformation DSLs is UTF-8. Transformers should only operate on native unicode text
unless additional processing, such as AST analysis, is absolutely required for the operation of the transformer. The
standard library includes a vast amount of introspection, parsing, compilation, and other tools prior to needing to
process and regenerate the whole source file from an abstraction. Any DSL whose purpose is the generation of text
should similarly default to UTF-8 output.


Encoding Naming Scheme
----------------------

DSLs may have flags and simple options associated with them. Due to limitations on the way Python searches for
encoding prefixes on source files, the names available are restricted.

1. Within the general name for a specific DSL, any alphanumeric characters (``a-z``, ``0-9``, regardless of case) may
   be used. This name is parsed early and used to look up the appropriate named metadata ``entry_point`` from the 
   ``marrow.dsl`` namespace. E.g.: ``cinje``

2. Allowed flags must be declared via ``FLAGS`` DSL metadata and are enabled within individual encoding declarations
   as suffixes on the name, with the same restrictions while allowing hyphens, each prefixed with a period. Multiple
   may be concatenated and should be lexicographically sorted. E.g. the ``raw`` and ``unsafe`` flags on the ``cinje``
   encoding: ``cinje.raw.unsafe``

3. Options are identified as hyphen-separated key value pairs. These are kept unambiguous from flags containing
   hyphens by the explicit declaration of allowed flags in the DSL metadata. Allowed options are defined through
   assignment of ``__slots__`` explicitly naming options to allocate storage for. (This causes Python to forbid
   assignment of unknown attributes.) While the value may contain hyphens, the key may not contain any.
   Numeric-seeming values will be cast to integers automatically during encoding declaration parsing.


Lines
-----

* ``Line`` defines the content, context, and metadata for a line of source input or transformed output. This includes
  such Python metadata as scope (denoted by indentation in the output), buffer membership, classification, or source
  line number.

* ``Lines`` represents a contextual buffer. Initially there are two: one representing the entirety of the source input,
  the other representing the translated output generated so far. As mentioned in the transformation summary below,
  block transformers may construct additional buffers to collect multiple lines while waiting for an exit condition
  (e.g. capturing function contents by entering on a ``def`` declaration, exiting on a reduction in scope).

Individual DSLs may override the specific Line and Lines implementations in use to further specialize behaviour.


Logical Lines
~~~~~~~~~~~~~

TBD

* common metadata
* extended metadata
* origin tracing
* continuation


Buffers
-------

TBD

* common metadata
* context stack
* reentrant FIFO, push to head mid-iteration
* named sections


Context
-------

* global metadata
* reentrant line producer
* named scopes


Engine Metadata
---------------

TBD


Engine Customization
--------------------

TBD


Transformation
--------------

Transformation is a stack-based, almost coroutine-like streaming process utilizing Python's yield syntax extensively. Individual transformers cooperate to construct the working context as they go, with block transformers manipulating whole lines, and inline transformers manipulating substrings of a line. Additionally, block transformers may be unbuffered, where they may generate one or more lines in response to a line, or buffered, where they act as context managers helping to subdivide the source text into logical sections by constructing "nested" (though not really) buffers.


Block Transformation
~~~~~~~~~~~~~~~~~~~~

TBD

* unbuffered
* buffered


Inline Transformation
~~~~~~~~~~~~~~~~~~~~~

TBD

* delimited interpolation


AST Transformation
~~~~~~~~~~~~~~~~~~

TBD

* buffer context exit triggered
* post other transformation on the buffer contents


Version History
===============

Version 1.0
-----------

* Initial release.


License
=======

Marrow DSL (``marrow.dsl``) has been released under the MIT Open Source license.

The MIT License
---------------

Copyright © 2011-2017 Alice Bevan-McGregor and contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

.. |ghwatch| image:: https://img.shields.io/github/watchers/marrow/dsl.svg?style=social&label=Watch
    :target: https://github.com/marrow/dsl/subscription
    :alt: Subscribe to project activity on Github.

.. |ghstar| image:: https://img.shields.io/github/stars/marrow/dsl.svg?style=social&label=Star
    :target: https://github.com/marrow/dsl/subscription
    :alt: Star this project on Github.

.. |ghfork| image:: https://img.shields.io/github/forks/marrow/dsl.svg?style=social&label=Fork
    :target: https://github.com/marrow/dsl/fork
    :alt: Fork this project on Github.

.. |masterstatus| image:: http://img.shields.io/travis/marrow/dsl/master.svg?style=flat
    :target: https://travis-ci.org/marrow/dsl/branches
    :alt: Release build status.

.. |mastercover| image:: http://img.shields.io/codecov/c/github/marrow/dsl/master.svg?style=flat
    :target: https://codecov.io/github/marrow/dsl?branch=master
    :alt: Release test coverage.

.. |masterreq| image:: https://img.shields.io/requires/github/marrow/dsl.svg
    :target: https://requires.io/github/marrow/dsl/requirements/?branch=master
    :alt: Status of release dependencies.

.. |developstatus| image:: http://img.shields.io/travis/marrow/dsl/develop.svg?style=flat
    :target: https://travis-ci.org/marrow/dsl/branches
    :alt: Development build status.

.. |developcover| image:: http://img.shields.io/codecov/c/github/marrow/dsl/develop.svg?style=flat
    :target: https://codecov.io/github/marrow/dsl?branch=develop
    :alt: Development test coverage.

.. |developreq| image:: https://img.shields.io/requires/github/marrow/dsl.svg
    :target: https://requires.io/github/marrow/dsl/requirements/?branch=develop
    :alt: Status of development dependencies.

.. |issuecount| image:: http://img.shields.io/github/issues-raw/marrow/dsl.svg?style=flat
    :target: https://github.com/marrow/dsl/issues
    :alt: Github Issues

.. |ghsince| image:: https://img.shields.io/github/commits-since/marrow/dsl/1.0.0.svg
    :target: https://github.com/marrow/dsl/commits/develop
    :alt: Changes since last release.

.. |ghtag| image:: https://img.shields.io/github/tag/marrow/dsl.svg
    :target: https://github.com/marrow/dsl/tree/1.0.0
    :alt: Latest Github tagged release.

.. |latestversion| image:: http://img.shields.io/pypi/v/marrow.dsl.svg?style=flat
    :target: https://pypi.python.org/pypi/marrow.dsl
    :alt: Latest released version.

.. |downloads| image:: http://img.shields.io/pypi/dw/marrow.dsl.svg?style=flat
    :target: https://pypi.python.org/pypi/marrow.dsl
    :alt: Downloads per week.

.. |cake| image:: http://img.shields.io/badge/cake-lie-1b87fb.svg?style=flat
