"""
Functions for exception manipulation + custom exceptions used by Snek to identify
common deviations from the expected behavior.
"""
import functools
import logging
import sys
import traceback
from pathlib import Path
from typing import Optional, Sequence, Union, cast

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import EntryPoint  # pragma: no cover
else:
    from importlib_metadata import EntryPoint  # pragma: no cover

from . import __version__ as snek_version


def exceptions2exit(exception_list):
    """Decorator to convert given exceptions to exit messages

    This avoids displaying nasty stack traces to end-users

    Args:
        exception_list [Exception]: list of exceptions to convert
    """

    def exceptions2exit_decorator(func):
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except tuple(exception_list) as ex:  # noqa: B030
                from .cli import get_log_level  # defer circular imports to avoid errors

                if get_log_level() <= logging.DEBUG:
                    # user surely wants to see the stacktrace
                    traceback.print_exc()
                print(f"ERROR: {ex}")
                sys.exit(1)

        return func_wrapper

    return exceptions2exit_decorator


class ActionNotFound(KeyError):
    """Impossible to find the required action."""

    def __init__(self, name, *args, **kwargs):
        message = ActionNotFound.__doc__[:-1] + f": `{name}`"
        super().__init__(message, *args, **kwargs)


class DirectErrorForUser(RuntimeError):
    """Parent class for exceptions that can be shown directly as error messages
    to the final users.
    """

    def __init__(self, message=None, *args, **kwargs):
        message = message or self.__class__.__doc__
        super().__init__(message, *args, **kwargs)


class DirectoryAlreadyExists(DirectErrorForUser):
    """The project directory already exists, but no ``update`` or ``force``
    option was used.
    """


class DirectoryDoesNotExist(DirectErrorForUser):
    """No directory was found to be updated."""


class GitNotInstalled(DirectErrorForUser):
    """Snek requires git to run."""

    DEFAULT_MESSAGE = (
        "Make sure git is installed and working. "
        "Use flag --very-verbose for more information."
    )

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class GitNotConfigured(DirectErrorForUser):
    """Snek tries to read user.name and user.email from git config."""

    DEFAULT_MESSAGE = (
        "Make sure git is configured. Run:\n"
        '  git config --global user.email "you@example.com"\n'
        '  git config --global user.name "Your Name"\n'
        "to set your account's default identity."
    )

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class GitDirtyWorkspace(DirectErrorForUser):
    """Workspace of git is empty."""

    DEFAULT_MESSAGE = (
        "Your working tree is dirty. Commit your changes first" " or use '--force'."
    )

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class InvalidIdentifier(RuntimeError):
    """Python requires a specific format for its identifiers.

    https://docs.python.org/3.6/reference/lexical_analysis.html#identifiers
    """


class SnekTooOld(DirectErrorForUser):
    """Snek cannot update a pre 3.0 version"""

    DEFAULT_MESSAGE = (
        "setup.cfg has no section [snek]! "
        "Are you trying to update a pre 3.0 version?"
    )

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class NoSnekProject(DirectErrorForUser):
    """Snek cannot update a project that it hasn't generated"""

    DEFAULT_MESSAGE = "Could not update project. Was it generated with Snek?"

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class ShellCommandException(RuntimeError):
    """Outputs proper logging when a ShellCommand fails"""


class ImpossibleToFindConfigDir(DirectErrorForUser):
    """An expected error occurred when trying to find the config dir.

    This might be related to not being able to read the $HOME env var in Unix
    systems, or %USERPROFILE% in Windows, or even the username.
    """


class ExtensionNotFound(DirectErrorForUser):
    """The following extensions were not found: {extensions}.
    Please make sure you have the required versions installed.
    """

    def __init__(self, extensions: Sequence[str]):
        message = cast(str, self.__doc__)
        message = message.format(extensions=extensions, version=snek_version)
        super().__init__(message)


class ErrorLoadingExtension(DirectErrorForUser):
    """There was an error loading '{extension}'.
    Please make sure you have installed a version of the extension that is compatible
    with Snek {version}. You can also try unininstalling it.
    """

    def __init__(self, extension: str = "", entry_point: Optional[EntryPoint] = None):
        if entry_point and not extension:
            extension = getattr(entry_point, "module", entry_point.name)

        if extension.endswith(".extension"):
            extension = extension[: -len(".extension")]
        extension = extension.replace("snekext.", "snekext-")

        message = cast(str, self.__doc__)
        message = message.format(extension=extension, version=snek_version)
        super().__init__(message)


class NestedRepository(DirectErrorForUser):
    """The directory '{directory}' is already part of a git repository.

    Snek avoids creating nested projects to prevent errors with
    `setuptools-scm`.

    If you know what you are doing you can try running `putup` again with
    the`--force` flag, but please be aware that you will have to manually
    customise the configuration for `setuptools-scm`. For more information,
    have a look on:

    - https://github.com/pypa/setuptools_scm
    """

    def __init__(self, directory: Union[str, Path]):
        message = cast(str, self.__doc__)
        super().__init__(message.format(directory=directory))
