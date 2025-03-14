import json
import os
import sys
from functools import partial
from pathlib import Path
from subprocess import CalledProcessError

import pytest

from snek import __version__ as snek_version
from snek.api import create_project
from snek.extensions.venv import Venv

from .helpers import find_venv_bin, run

pytestmark = [pytest.mark.slow, pytest.mark.system]


@pytest.fixture(autouse=True)
def dont_load_dotenv(monkeypatch):
    """pytest-virtualenv creates a `.env` directory by default, but `.env`
    entries in the file system are loaded by Pipenv as dotenv files.

    To prevent errors for happening we have to disable this feature.

    Additionally, it seems that env vars have to be changed before using
    venv, so an autouse fixture is required (cannot put this part in the
    beginning of the test function.
    """
    monkeypatch.setenv("PIPENV_DONT_LOAD_ENV", "1")
    monkeypatch.setenv("PIPENV_IGNORE_VIRTUALENVS", "1")
    monkeypatch.setenv("PIP_IGNORE_INSTALLED", "1")
    monkeypatch.setenv("PIPENV_VERBOSITY", "-1")


@pytest.mark.skipif(
    os.name == "nt", reason="pipenv fails due to colors (non-utf8) under Windows 10"
)
def test_pipenv_works_with_snek(tmpfolder, monkeypatch, venv):
    # Given a project is created with snek
    # and it has some dependencies in setup.cfg
    create_project(project_path="myproj", requirements=["platformdirs"])

    if any(ch in snek_version for ch in ("b", "a", "pre", "rc")):
        flags = "--pre"
    else:
        flags = ""

    with tmpfolder.join("myproj").as_cwd():
        # When we install pipenv,
        venv.run("pip install -v pipenv")

        try:
            venv.run("pipenv --bare install certifi")
            # use it to proxy setup.cfg
            venv.run(f"pipenv --bare install {flags} -e .")
            # and install things to the dev env,
            venv.run("pipenv --bare install --dev flake8")
            # Then it should be able to generate a Pipfile.lock
            venv.run("pipenv lock")
        except Exception:
            if sys.version_info[:2] <= (3, 6):
                # TODO: Remove try...except when 3.6 is no longer supported
                pytest.skip("Skip Pipenv specific problem for 3.6")
            else:
                raise

        assert Path("Pipfile.lock").exists()

        # with the correct dependencies
        with open("Pipfile.lock") as fp:
            content = json.load(fp)
            assert content["default"]["platformdirs"]
            assert content["develop"]["flake8"]

        # and run things from inside pipenv's venv
        pipenv_path = venv.run("pipenv --venv")
        assert pipenv_path in venv.run("pipenv run which flake8")
        venv.run("pipenv --bare run flake8 src/myproj/cli.py")


@pytest.mark.xfail(
    sys.version_info < (3, 7), reason="pip-compile may fail in old Python"
)
def test_piptools_works_with_snek(tmpfolder, monkeypatch):
    venv_path = Path(str(tmpfolder), "myproj/.venv").resolve()
    find = partial(find_venv_bin, venv_path)
    # Given a project is created with snek
    # and it has some dependencies in setup.cfg
    create_project(
        project_path="myproj", extensions=[Venv()], requirements=["platformdirs"]
    )
    with tmpfolder.join("myproj").as_cwd():
        requirements_in = Path("requirements.in")
        # When we install pip-tools
        run(f"{find('python')} -m pip install -v pip-tools certifi")
        # and write a requirements.in file that proxies setup.cfg
        # and install other things,
        requirements_in.write_text("-e file:.\nflake8")
        # Then we should be able to generate a requirements.txt
        run(find("pip-compile"))
        requirements_txt = Path("requirements.txt")
        assert requirements_txt.exists()
        # with the correct dependencies
        content = requirements_txt.read_text()
        assert "platformdirs==" in content
        assert "flake8==" in content
        assert "file:." in content
        # install the dependencies
        # and run things from inside pipenv's venv
        pip_sync = find("pip-sync")
        try:
            # pip-tools have problems on windows inside a test env with relative paths
            run(pip_sync)
            run(f"{find('flake8')} src/myproj/cli.py")
        except CalledProcessError as ex:
            if "assert" in ex.output:
                pytest.skip(
                    "pip-tools tries to assert a path is absolute, which fails "
                    "inside test env for some OSs"
                )
            else:
                raise
