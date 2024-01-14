Action Pipeline
===============

Snek organizes the generation of a project into a series of steps with
well defined purposes. As shown in the figure below,
each step is called **action** and is implemented as a
simple function that receives two arguments: a project structure and a :obj:`dict`
with options (some of them parsed from command line arguments, other from
default values).

.. image:: gfx/action-pipeline-paths.svg
   :alt: Snek's action pipeline
   :align: center

An action **MUST** return a tuple also composed by a project structure and a
:obj:`dict` with options. The return values, thus, are usually modified versions
of the input arguments. Additionally an action can also have side effects, like
creating directories or adding files to version control. The following
pseudo-code illustrates a basic action:

.. code-block:: python

    def action(project_structure, options):
        new_struct, new_opts = modify(project_structure, options)
        some_side_effect()
        return new_struct, new_opts

The output of each action is used as the input of the subsequent action,
forming a pipeline. Initially the structure argument is just an empty :obj:`dict`.
Each action is uniquely identified by a string in the format
``<module name>:<function name>``, similarly to the convention used for a
`setuptools entry point`_.
For example, if an action is defined in the ``action`` function of the
``extras.py`` file that is part of the ``snekext.contrib`` project,
the **action identifier** is ``snekext.contrib.extras:action``.

By default, the sequence of actions taken by Snek is:

#. :obj:`snek.actions:get_default_options <snek.actions.get_default_options>`
#. :obj:`snek.actions:verify_options_consistency <snek.actions.verify_options_consistency>`
#. :obj:`snek.structure:define_structure <snek.structure.define_structure>`
#. :obj:`snek.actions:verify_project_dir <snek.actions.verify_project_dir>`
#. :obj:`snek.update:version_migration <snek.update.version_migration>`
#. :obj:`snek.structure:create_structure <snek.structure.create_structure>`
#. :obj:`snek.actions:init_git <snek.actions.init_git>`
#. :obj:`snek.actions:report_done <snek.actions.report_done>`

(as given by :obj:`snek.actions.DEFAULT`)

The project structure is usually empty until :obj:`~snek.structure.define_structure`
This action just loads the in-memory :obj:`dict` representation, that is only written
to disk by the :obj:`~snek.structure.create_structure` action.

Note that, this sequence varies according to the command line options.
To retrieve an updated list, please use ``putup --list-actions`` or
``putup --dry-run``.


.. _setuptools entry point: https://setuptools.pypa.io/en/stable/userguide/entry_point.html
