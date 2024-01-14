Snek is a project generator for bootstrapping high quality Python packages,
ready to be shared on PyPI_ and installable via pip_. It is easy to use and
encourages the adoption of the best tools and practices of the Python
ecosystem, helping you and your team to stay sane, happy and productive. The
best part? It is stable and has been used by thousands of developers for over
half a decade!

Quickstart
==========

Just pick your favourite installation method::

    pip install snek 

If you want to install all Snek's *extensions* you can even::

    pip install snek[all]

(More details of each method are available in the `installation docs`_)

After the installation, a new ``snek`` command will be available and you can just type::

    snek my_project

This will create a new folder called ``my_project`` containing a perfect *project
template* with everything you need for some serious coding.

After ``cd``-ing into your new project and creating (or activating) an `isolated
development environment`_ (with virtualenv_, conda_ or your preferred tool),
you can do the usual `editable install`_::

    pip install -e .

… all set and ready to go!

We also recommend using tox_, so you can take advantage of the automation tasks
we have setup for you, like::

   tox -e build  # to build your package distribution
   tox -e publish  # to test your project uploads correctly in test.pypi.org
   tox -e publish -- --repository pypi  # to release your package to PyPI
   tox -av  # to list all the tasks available

The following figure demonstrates the usage of ``snek`` with the new experimental
interactive mode for setting up a simple project.
It uses the `--cirrus` flag to add CI support (via `Cirrus CI`_), and
tox_ to run automated project tasks like building a package file for
distribution (or publishing).

Type ``snek -h`` to learn about more configuration options. Snek assumes
that you have Git_ installed and set up on your PC,
meaning at least your name and email are configured.

The project template provides you with following features:


Configuration & Packaging
=========================

All configuration can be done in ``setup.cfg`` like changing the description,
URL, classifiers, installation requirements and so on as defined by setuptools_.
That means in most cases it is not necessary to tamper with ``setup.py``.

In order to build a source or wheel distribution, just run ``tox -e build``
(if you don't use tox_, you can also install ``build`` and run ``python -m build``).

.. rubric:: Package and Files Data

Additional data, e.g. images and text files, that reside within your package and
are tracked by Git will automatically be included
if ``include_package_data = True`` in ``setup.cfg``.
It is not necessary to have a ``MANIFEST.in`` file for this to work.

Note that the ``include_package_data`` option in ``setup.cfg`` is only
guaranteed to be read when creating a `wheels`_ distribution. Other distribution methods might
behave unexpectedly (e.g. always including data files even when
``include_package_data = False``). Therefore, the best option if you want to have
data files in your repository **but not as part of the pip installable package**
is to add them somewhere **outside** the ``src`` directory (e.g. a ``files``
directory in the root of the project, or inside ``tests`` if you use them for
checks). Additionally you can exclude them explicitly via the
``[options.packages.find] exclude`` option in ``setup.cfg``.


Versioning and Git Integration
==============================

Your project is an already initialised Git repository and uses
the information of tags to infer the version of your project with the help of
setuptools_scm_.
To use this feature, you need to tag with the format ``MAJOR.MINOR[.PATCH]``
, e.g. ``0.0.1`` or ``0.1``.
This version will be used when building a package and is also accessible
through ``my_project.__version__``.

Unleash the power of Git by using its `pre-commit hooks`_. This feature is
available through the ``--pre-commit`` flag. After your project's scaffold
was generated, make sure pre-commit is installed, e.g. ``pip install pre-commit``,
then just run ``pre-commit install``.

A default ``.gitignore`` file is also provided; it is
well adjusted for Python projects and the most common tools.


Sphinx Documentation
====================

Snek will prepare a `docs` directory with all you need to start writing
your documentation.
Start editing the file ``docs/index.rst`` to extend the documentation.
The documentation also works with `Read the Docs`_.

The `Numpy and Google style docstrings`_ are activated by default.

If you have `tox`_ in your system, simply run ``tox -e docs`` or ``tox -e
doctests`` to compile the docs or run the doctests.

Alternatively, if you have `make`_ and `Sphinx`_ installed in your computer, build the
documentation with ``make -C docs html`` and run doctests with
``make -C docs doctest``. Just make sure Sphinx 1.3 or above is installed.


Automation, Tests & Coverage
============================

Snek relies on `pytest`_ to run all automated tests defined in the subfolder
``tests``.  Some sane default flags for pytest are already defined in the
``[tool:pytest]`` section of ``setup.cfg``. The pytest plugin `pytest-cov`_ is used
to automatically generate a coverage report. It is also possible to provide
additional parameters and flags on the commandline, e.g., type::

    pytest -h

to show the help of pytest (requires `pytest`_ to be installed in your system
or virtualenv).

Projects generated with Snek by default support running tests via `tox`_,
a virtualenv management and test tool, which is very handy. If you run::

    tox

in the root of your project, `tox`_ will download its dependencies, build the
package, install it in a virtualenv and run the tests using `pytest`_, so you
are sure everything is properly tested.


.. rubric:: JUnit and Coverage HTML/XML

For usage with a continuous integration software JUnit and Coverage XML output
can be activated in ``setup.cfg``. Use the flag ``--cirrus`` to generate
templates of the `Cirrus CI`_ configuration file ``.cirrus.yml`` which even
features the coverage and stats system `Coveralls`_.


Management of Requirements & Licenses
=====================================

Installation requirements of your project can be defined inside ``setup.cfg``,
e.g. ``install_requires = numpy; scipy``. To avoid package dependency problems
it is common to not pin installation requirements to any specific version,
although minimum versions, e.g. ``sphinx>=1.3``, and/or maximum versions, e.g.
``pandas<0.12``, are used frequently in accordance with `semantic versioning`_.

All licenses from `choosealicense.com`_ can be easily selected with the help
of the ``--license`` flag.


Easy Updating
=============

Keep your project up-to-date by applying
``snek --update my_project`` when a new version of Snek was released.
An update will only overwrite files that are not often altered by users like
``setup.py``. To update all files use ``--update --force``.
An existing project that was not setup with Snek can be converted with
``snek --force existing_project``. The force option is completely safe to use
since the git repository of the existing project is not touched!
