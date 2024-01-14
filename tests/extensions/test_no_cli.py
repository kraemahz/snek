#!/usr/bin/env python
import sys
from pathlib import Path

from snek.api import create_project
from snek.cli import run
from snek.extensions import no_cli


def test_create_project_wit_no_cli(tmpfolder):
    # Given options with the no-cli extension,
    opts = dict(project_path="proj", extensions=[no_cli.NoSkeleton("no-cli")])

    # when the project is created,
    create_project(opts)

    # then cli file should not exist
    assert not Path("proj/src/proj/cli.py").exists()
    assert not Path("proj/tests/test_cli.py").exists()


def test_create_project_without_no_cli(tmpfolder):
    # Given options without the no-cli extension,
    opts = dict(project_path="proj")

    # when the project is created,
    create_project(opts)

    # then cli file should exist
    assert Path("proj/src/proj/cli.py").exists()
    assert Path("proj/tests/test_cli.py").exists()


def test_cli_with_no_cli(tmpfolder):
    # Given the command line with the no-cli option,
    sys.argv = ["snek", "--no-cli", "proj"]

    # when snek runs,
    run()

    # then cli file should not exist
    assert not Path("proj/src/proj/cli.py").exists()
    assert not Path("proj/tests/test_cli.py").exists()


def test_cli_with_no_cli_and_pretend(tmpfolder):
    # Given the command line with the no-cli and pretend options,
    sys.argv = ["snek", "--pretend", "--no-cli", "proj"]

    # when snek runs,
    run()

    # then cli file should not exist (or the project itself)
    assert not Path("proj/src/proj/cli.py").exists()
    assert not Path("proj").exists()


def test_cli_without_no_cli(tmpfolder):
    # Given the command line without the no-cli option,
    sys.argv = ["snek", "proj"]

    # when snek runs,
    run()

    # then cli file should exist
    assert Path("proj/src/proj/cli.py").exists()
    assert Path("proj/tests/test_cli.py").exists()
