#!/usr/bin/env python
import sys
from pathlib import Path

from snek.api import create_project
from snek.cli import run
from snek.extensions.no_tox import NoTox


def test_create_project_with_tox(tmpfolder):
    # when the project is created,
    opts = dict(project_path="proj")
    create_project(opts)

    # then tox files are created by default
    assert Path("proj/tox.ini").exists()


def test_create_project_without_tox(tmpfolder):
    # when the project is created with no_tox
    opts = dict(project_path="proj", extensions=[NoTox()])
    create_project(opts)

    # then tox files should not exist
    assert not Path("proj/tox.ini").exists()


def test_cli_with_tox(tmpfolder):
    # when the project is created with the CLI
    sys.argv = ["snek", "proj"]
    run()

    # then tox files should exist
    assert Path("proj/tox.ini").exists()


def test_cli_without_tox(tmpfolder):
    # Given the command line with --no-tox
    sys.argv = ["snek", "proj", "-vv", "--no-tox"]

    # when snek runs,
    run()

    # then tox files should not exist
    assert not Path("proj/tox.ini").exists()


def test_cli_without_tox_but_pretend(tmpfolder):
    # Given the command line with --no-tox and --pretend
    sys.argv = ["snek", "proj", "-vv", "--no-tox", "--pretend"]

    # when snek runs,
    run()

    # then tox files should not exist (or even the project)
    assert not Path("proj/tox.ini").exists()
    assert not Path("proj").exists()
