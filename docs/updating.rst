.. _updating:

===============================
Updating from Previous Versions
===============================

When updating a project generated with the same major version of Snek
[#up1]_, running ``putup --update`` should be enough to get you going.
However updating from previous major versions of Snek will probably
require some manual adjustments. The following sections describe how to update
from one major version into the following one.

.. tip::
   Before updating make sure to commit all the pending changes in your
   repository. If something does not work exactly how you expected after the
   update, please revise the changes using a ``diff`` and perform the necessary
   corrections.


Updates from Snek 2 to Snek 3
-----------------------------------------

Since the overall structure of a project set up with Snek 2 differs quite
much from a project generated with Snek 3 it is not possible to just use
the ``--update`` parameter. Still with some manual efforts an update from
a scaffold generated with Snek 2 to Snek 3's scaffold is quite easy.
Assume the name of our project is ``old_project`` with a package called
``old_package`` and no namespaces then just:

1) make sure your worktree is not dirty, i.e. commit all your changes,
2) run ``putup old_project --force --no-cli -p old_package`` to generate
   the new structure inplace and ``cd`` into your project,
3) move with ``git mv old_package/* src/old_package/ --force`` your old package
   over to the new ``src`` directory,
4) check ``git status`` and add untracked files from the new structure,
5) use ``git difftool`` to check all overwritten files, especially ``setup.cfg``,
   and transfer custom configurations from the old structure to the new,
6) check if ``python setup.py test sdist`` works and commit your changes.


Updates from Snek 3 to Snek 4
-----------------------------------------

**Most of the time, updating from Snek 3 should be completely automatic**.
However, since in version 4 we have adopted Python's new standards for
packaging (:pep:`517`/:pep:`518`), you might find the new build process incompatible.

.. _no-pyproject-steps:

If that is the case, you might want to try reverting to the legacy behaviour
and preventing the build tools from using isolated builds (:pep:`517`).
That can be easily done by deleting the `pyproject.toml` file from your package
root.

You will need, though, to manually follow a few extra steps to make sure
everything works:

1) Remove Snek from your build dependencies (``setup_requires`` in ``setup.cfg``)
   and add `setuptools-scm`_.

   .. note::
      The use of ``setup_requires`` is discouraged. When updating to v4
      Snek will remove this field automatically and transfer the
      dependencies to the ``pyproject.toml :: build-system.requires`` field,
      which means you may need to manually place them back when deleting
      ``pyproject.toml``.
      Alternatively you can ditch ``setup_requires`` completely and
      rely on other tools like `tox`_ or `make`_ to build your
      project with the correct dependencies in place inside a virtual
      environment. This have the advantage of increasing reproducibility.
      With `tox`_ you can specify a ``build`` testenv with the `skip_install`_
      option and the required build time dependencies listed in ``deps``.

2) Migrate any configuration options for tools that might be
   using ``pyproject.toml`` to alternative files. For example if you have
   ``isort`` and ``coverage`` configurations in your ``pyproject.toml``, you
   might want to rewrite them in the |isortcfg|_ and |coveragerc|_ files respectively.

3) Please open an issue with Snek so we understand with kind of backward
   incompatibilities :pep:`517` and :pep:`518` might be causing and try to help.
   Similarly you might also consider opening an issue with setuptools_.

.. warning::
   For the time being you can use the **transitional** ``--no-pyproject``
   option, when running ``putup``, but have in mind that this option will
   be removed in future versions of Snek.

Snek 4 also adopts the :pep:`420` scheme for implicit namespaces and will
automatically migrate existing packages. This is incompatible with the
previously adopted `pkg_resources`_ methodology. **Fortunately, this will not
affect you if you are not using namespaces**, but in the case you are,
installing a new :pep:`420`-compliant package in an environment that already
contains other packages with the same namespace but that use the
`pkg_resources`_ methodology, will likely result in errors (please check the
`official packaging namespace packages guides`_ for more information).

To solve this problem you will need to either migrate the existing
packages to :pep:`420` or revert some specific configurations in ``setup.cfg``
after the update. In particular ``packages = find_namespace:`` should
be converted back to ``packages = find:`` in the ``[options]`` section (use
a ``git difftool`` to help you with that).
If using `Sphinx`_ for the documentation, you can also remove the
``--implicit-namespaces`` option in the ``cmd_line_template`` variable in the
``docs/conf.py`` file.

.. tip::
   Existing regular Python files (or other directories containing Python files)
   that do not belong to the package distribution but are placed inside the
   ``src`` folder (such as example files not meant to be packaged), can cause
   problems when building your package.

   Please move these files if necessary to their own separated folders (e.g.
   the ``docs`` folder or a new ``examples`` folder in the root of the
   repository), or revert back to the `pkg_resources`_ implementation. Just
   have in mind that Snek, considers the ``src`` directory to be
   exclusively dedicated to store files meant to be distributed, and will rely
   on that assumption on its future versions and updates.


.. [#up1] Snek uses 3 numbers for its version: ``MAJOR.MINOR.PATCH``
   (when the numbers on the right are missing, just assume them as being 0),
   so Snek 3.1.2 has the same major version as Snek 3.3.1, but not
   Snek 4.

.. |isortcfg| replace:: *.isort.cfg*
.. |coveragerc| replace:: *.coveragerc*

.. _setuptools-scm: https://pypi.org/project/setuptools-scm/
.. _tox: https://tox.wiki/en/stable/
.. _make: https://www.gnu.org/software/make/manual/html_node/index.html
.. _skip_install: https://tox.wiki/en/stable/config.html#skip_install
.. _official packaging namespace packages guides: https://packaging.python.org/guides/packaging-namespace-packages/
.. _pkg_resources: https://setuptools.pypa.io/en/stable/pkg_resources.html
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _isortcfg: https://pycqa.github.io/isort/docs/configuration/config_files
.. _coveragerc: https://coverage.readthedocs.io/en/coverage-5.1/config.html
.. _setuptools: https://github.com/pypa/setuptools/issues
