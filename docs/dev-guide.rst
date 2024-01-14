===============
Developer Guide
===============


This document describes the internal architecture and the main concepts behind
Snek. It assumes the reader has some experience in *using* Snek
(specially its command line interface, ``putup``) and some familiarity with `Python's
package ecosystem`_.

Please notice this document does not target Snek's users, instead it
provides **internal** documentation for those who are involved in Snek's
development.


.. _core-concepts:

Architecture
============

As indicated in the figure below, Snek can be divided in two main
execution blocks: a pure Python API and the command line interface wrapping
it as an executable program that runs on the shell.

.. image:: gfx/api-paths.svg
   :alt: Snek's architecture
   :align: center

The CLI is responsible for defining all arguments ``putup``
accepts and parsing the user input accordingly. The result is a :obj:`dict`
that contains options expressing the user preference and can be fed
into Snek's main API, :obj:`~snek.api.create_project`.

This function is responsible for combining the provided options :obj:`dict`
with pre-existing project configurations that might be available in the project
directory (the ``setup.cfg`` file, if present) and globally defined default
values (via :ref:`Snek's own configuration file <configuration>`).
It will then create an (initially empty) *in-memory* representation of the
project structure and run Snek's action pipeline, which in turn will
(between other tasks) write customized versions of Snek's templates to
the disk as project files, according to the combined scaffold options.

The project representation and the action pipeline are two key concepts in
Snek's architecture and are described in detail in the following
sections.

.. _project-structure:
.. include:: project-structure.rst

.. _action-pipeline:
.. include:: action-pipeline.rst


Extensions
==========

Extensions are a mechanism provided by Snek to modify its action pipeline
at runtime and the preferred way of adding new functionality.
There are **built-in extensions** (e.g. :mod:`snek.extensions.cirrus`)
and **external extensions** (e.g. `snekext-dsproject`_), but both types
of extensions work exactly in the same way.
This division is purely based on the fact that some of Snek features are
implemented as extensions that ship by default with the ``snek`` package,
while other require the user to install additional Python packages.

Extensions are required to add at least one CLI argument that allow the users
to opt-in for their behaviour. When ``putup`` runs, Snek's will
dynamically discover installed extensions via `setuptools entry points`_ and
add their defined arguments to the main CLI parser. Once activated, a
extension can use the helper functions defined in :mod:`snek.actions` to
manipulate Snek's action pipeline and therefore the project structure.

For more details on extensions, please consult our :ref:`Extending Snek
<extensions>` guide.


Code base Organization
======================

Snek is organized in a series of internal Python modules, the main ones
being:

- :mod:`~snek.api`: top level functions for accessing Snek
  functionality, by combining together the other modules
- :mod:`~snek.cli`: wrapper around the API to create a command
  line executable program
- :mod:`~snek.actions`: default action pipeline and helper functions for
  manipulating it
- :mod:`~snek.structure`: functions specialized in defining the in-memory
  project structure representation and in taking this representation and
  creating it as part of the file system.
- :mod:`~snek.update`: steps required for updating projects generated
  with old versions of Snek
- :mod:`~snek.extensions`: main extension mechanism and subpackages
  corresponding to the built-in extensions

Additionally, a series of internal auxiliary libraries is defined in:

- :mod:`~snek.dependencies`: processing and manipulating of package
  dependencies and requirements
- :mod:`~snek.exceptions`: custom Snek exceptions and exception handlers
- :mod:`~snek.file_system`: wrappers around file system functions that
  make them easy to be used from Snek.
- :mod:`~snek.identification`: creating and processing of
  project/package/function names and other general identifiers
- :mod:`~snek.info`: general information about the system, user and
  package being generated
- :mod:`~snek.log`: custom logging infrastructure for Snek,
  specialized in its verbose execution
- :mod:`~snek.operations`: file operations that can be
  embedded in the in-memory project structure representation
- :mod:`~snek.repo`: wrapper around the ``git`` command
- :mod:`~snek.shell`: helper functions for working with external programs
- :mod:`~snek.termui`: basic support for ANSI code formatting
- :mod:`~snek.toml`: thin adapter layer around third-party TOML parsing
  libraries, focused in API stability

For more details about each module and its functions and classes, please
consult our :doc:`module reference <api/modules>`.

.. _Python's package ecosystem: https://packaging.python.org
.. _setuptools entry points: https://setuptools.pypa.io/en/stable/userguide/entry_point.html
.. _article about naming smells: https://hilton.org.uk/blog/naming-smells
.. _presentation aboug how to name things: https://hilton.org.uk/presentations/naming
