import logging
import os
import sys
from distutils.util import strtobool
from importlib import reload
from pathlib import Path
from tempfile import mkdtemp
from types import SimpleNamespace as Object

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib import metadata
else:
    import importlib_metadata as metadata

import pytest

from .helpers import (
    command_exception,
    disable_import,
    nop,
    replace_import,
    rmpath,
    uniqstr,
)
from .virtualenv import VirtualEnv

IS_POSIX = os.name == "posix"


def _config_git(home):
    config = """
        [user]
          name = Jane Doe
          email = janedoe@email
    """
    (home / ".gitconfig").write_text(config)


def _fake_expanduser(original_expand, real_home, fake_home):
    def _expand(path):
        value = original_expand(path)
        if value.startswith(str(fake_home)):
            return value

        return value.replace(str(real_home), str(fake_home))

    return _expand


@pytest.fixture(autouse=True)
def fake_home(tmp_path, monkeypatch):
    """Isolate tests.
    Avoid interference of an existing config dir in the developer's
    machine
    """
    real_home = os.getenv("REAL_HOME")
    home = os.getenv("HOME")
    if real_home and real_home != home:
        # Avoid doing it twice
        yield home
        return

    real_home = str(os.path.expanduser("~"))
    monkeypatch.setenv("REAL_HOME", real_home)

    fake = Path(mkdtemp(prefix="home", dir=str(tmp_path)))
    _config_git(fake)

    expanduser = _fake_expanduser(os.path.expanduser, real_home, fake)
    monkeypatch.setattr("os.path.expanduser", expanduser)
    monkeypatch.setenv("HOME", str(fake))
    monkeypatch.setenv("USERPROFILE", str(fake))  # Windows?

    yield fake
    rmpath(fake)


@pytest.fixture(autouse=True)
def fake_xdg_config_home(fake_home, monkeypatch):
    """Isolate tests.
    Avoid interference of an existing config dir in the developer's
    machine
    """
    home = str(fake_home)
    monkeypatch.setenv("XDG_CONFIG_HOME", home)
    yield home


@pytest.fixture(autouse=True)
def fake_config_dir(request, tmp_path, monkeypatch):
    """Isolate tests.
    Avoid interference of an existing config dir in the developer's
    machine
    """
    if "no_fake_config_dir" in request.keywords:
        # Some tests need to check the original implementation to make sure
        # side effects of the shared object are consistent. We have to try to
        # make them as few as possible.
        yield
        return

    confdir = Path(mkdtemp(prefix="conf", dir=str(tmp_path)))
    monkeypatch.setattr("snek.info.config_dir", lambda *_, **__: confdir)
    yield confdir
    rmpath(confdir)


@pytest.fixture
def venv(tmp_path, fake_home, fake_xdg_config_home):
    """Create a virtualenv for each test"""
    virtualenv = VirtualEnv(".venv", tmp_path)
    virtualenv.env["HOME"] = str(fake_home)
    virtualenv.env["USERPROFILE"] = str(fake_home)
    virtualenv.env["XDG_CONFIG_HOME"] = str(fake_xdg_config_home)

    trusted = os.environ.get("PIP_TRUSTED_HOST")
    if trusted:
        virtualenv.env["PIP_TRUSTED_HOST"] = trusted

    cache = os.environ.get("PIP_CACHE")
    if cache:
        virtualenv.env["PIP_CACHE"] = cache

    virtualenv.create()

    return virtualenv


@pytest.fixture
def existing_venv(venv):
    """Alias of ``venv`` to avoid clashes with ``snek.extensions.venv``"""
    return venv


@pytest.fixture
def snek():
    return __import__("snek")


@pytest.fixture
def real_isatty():
    snek = __import__("snek", globals(), locals(), ["termui"])
    return snek.termui.isatty


@pytest.fixture
def logger(monkeypatch):
    snek = __import__("snek", globals(), locals(), ["log"])
    logger_obj = snek.log.logger
    monkeypatch.setattr(logger_obj, "propagate", True)  # <- needed for caplog
    yield logger_obj


@pytest.fixture
def with_coverage():
    return strtobool(os.environ.get("COVERAGE", "NO"))


@pytest.fixture(autouse=True)
def isolated_logger(request, logger, monkeypatch):
    # In Python the common idiom of using logging is to share the same log
    # globally, even between threads. While this is usually OK because
    # internally Python takes care of locking the shared resources, it also
    # makes very difficult to build things on top of the logging system without
    # using the same global approach.
    # For simplicity, to make things easier to extension developers and because
    # Snek not really uses multiple threads, this is the case in
    # `snek.log`.
    # On the other hand, shared state and streams can make the testing
    # environment a real pain, since we are messing with everything all the
    # time, specially when running tests in parallel (so we not guarantee the
    # execution order).
    # This fixture do a huge effort in trying to isolate as much as possible
    # each test function regarding logging. We keep the global object, so the
    # tests can be seamless, but internally replace the underlying native
    # loggers and handlers for "one-shot" ones.
    # (Of course, we can keep the same global object just because the plugins
    # for running tests in parallel are based in multiple processes instead of
    # threads, otherwise we would need another strategy)

    if "original_logger" in request.keywords:
        # Some tests need to check the original implementation to make sure
        # side effects of the shared object are consistent. We have to try to
        # make them as few as possible.
        yield logger
        return

    # Get a fresh new logger, not used anywhere
    raw_logger = logging.getLogger(uniqstr())
    # ^  Python docs advert against instantiating Loggers directly and instruct
    #    devs to use `getLogger`. So we use a unique name to guarantee we get a
    #    new logger each time.
    raw_logger.setLevel(logging.NOTSET)
    new_handler = logging.StreamHandler()

    # Replace the internals of the LogAdapter
    # --> Messing with global state: don't try this at home ...
    #     (if we start to use threads, we cannot do this)

    # Be lazy to import modules due to coverage warnings
    # (see @FlorianWilhelm comments on #174)
    from snek.log import ReportFormatter

    monkeypatch.setattr(logger, "propagate", True)
    monkeypatch.setattr(logger, "nesting", 0)
    monkeypatch.setattr(logger, "wrapped", raw_logger)
    monkeypatch.setattr(logger, "handler", new_handler)
    monkeypatch.setattr(logger, "formatter", ReportFormatter())
    # <--

    try:
        yield logger
    finally:
        new_handler.close()
        # ^  Force the handler to not be re-used


@pytest.fixture
def tmpfolder(tmpdir):
    with tmpdir.as_cwd():
        yield tmpdir

    rmpath(tmpdir)


@pytest.fixture
def git_mock(monkeypatch, logger):
    def _git(*args, **kwargs):
        cmd = " ".join(["git"] + list(args))

        logger.report("run", cmd, context=os.getcwd())

        def _response():
            yield "git@mock"

        return _response()

    def _is_git_repo(folder):
        return Path(folder, ".git").is_dir()

    monkeypatch.setattr("snek.shell.git", _git)
    monkeypatch.setattr("snek.repo.is_git_repo", _is_git_repo)

    yield _git


@pytest.fixture
def nogit_mock(monkeypatch):
    def raise_error(*_):
        raise command_exception("No git mock!")

    monkeypatch.setattr("snek.shell.git", raise_error)
    yield


@pytest.fixture
def nogit_cmd_mock(monkeypatch):
    # With this fixture we still allow all the code paths in `get_git_cmd` to be
    # traversed during tests, so we improve the chances of catching errors.
    monkeypatch.setattr("snek.shell._GIT_CMD", "git-cmd.not-installed")
    monkeypatch.setattr("snek.shell._GIT_CMD_WIN", "git-cmd.not-installed.exe")

    from snek import shell

    shell.get_git_cmd.cache_clear()  # force reloading _GIT_CMD
    yield
    shell.get_git_cmd.cache_clear()  # force reloading _GIT_CMD


@pytest.fixture
def noconfgit_mock(monkeypatch):
    def raise_error(*argv):
        if "config" in argv:
            raise command_exception("No git mock!")

    monkeypatch.setattr("snek.shell.git", raise_error)
    yield


@pytest.fixture
def nodjango_admin_mock(monkeypatch):
    def raise_error(*_):
        raise command_exception("No django_admin mock!")

    monkeypatch.setattr("snek.shell.django_admin", raise_error)
    yield


@pytest.fixture
def nosphinx_mock():
    with disable_import("sphinx"):
        yield


@pytest.fixture
def version_raises_exception(monkeypatch, snek):
    def raise_exeception(name):
        raise metadata.PackageNotFoundError("No version mock")

    monkeypatch.setattr(metadata, "version", raise_exeception)
    reload(snek)
    try:
        yield
    finally:
        monkeypatch.undo()
        reload(snek)


@pytest.fixture(autouse=True)
def no_isatty(monkeypatch, real_isatty):
    # Requiring real_isatty ensures processing that fixture
    # before this one. Therefore real_isatty is cached before the mock
    # replaces the real function.

    # Avoid ansi codes in tests, since capture fixtures seems to
    # emulate stdout and stdin behavior (including isatty method)
    monkeypatch.setattr("snek.termui.isatty", lambda *_: False)
    yield


@pytest.fixture
def orig_isatty(monkeypatch, real_isatty):
    monkeypatch.setattr("snek.termui.isatty", real_isatty)
    yield real_isatty


@pytest.fixture
def no_curses_mock():
    with disable_import("curses"):
        yield


@pytest.fixture
def curses_mock():
    with replace_import("curses", Object()):
        yield


@pytest.fixture
def no_colorama_mock():
    with disable_import("colorama"):
        yield


@pytest.fixture
def colorama_mock():
    with replace_import("colorama", Object(init=nop)):
        yield
