#!/usr/bin/env python
import sys
from os.path import exists as path_exists

from snek.api import create_project
from snek.cli import run
from snek.extensions.cirrus import Cirrus


def test_create_project_with_cirrus(tmpfolder):
    # Given options with the cirrus extension,
    opts = dict(project_path="proj", extensions=[Cirrus("cirrus")])

    # when the project is created,
    create_project(opts)

    # then files from cirrus extension should exist
    assert path_exists("proj/.cirrus.yml")


def test_create_project_without_cirrus(tmpfolder):
    # Given options without the cirrus extension,
    opts = dict(project_path="proj")

    # when the project is created,
    create_project(opts)

    # then cirrus files should not exist
    assert not path_exists("proj/.cirrus.yml")


def test_cli_with_cirrus(tmpfolder):
    # Given the command line with the cirrus option,
    sys.argv = ["snek", "--cirrus", "proj"]

    # when snek runs,
    run()

    # then files from cirrus and other extensions automatically added should
    # exist
    assert path_exists("proj/.cirrus.yml")
    assert path_exists("proj/tox.ini")
    assert path_exists("proj/.pre-commit-config.yaml")


def test_cli_with_cirrus_and_pretend(tmpfolder):
    # Given the command line with the cirrus and pretend options
    sys.argv = ["snek", "--pretend", "--cirrus", "proj"]

    # when snek runs,
    run()

    # then cirrus files should not exist
    assert not path_exists("proj/.cirrus.yml")
    # (or the project itself)
    assert not path_exists("proj")


def test_cli_without_cirrus(tmpfolder):
    # Given the command line without the cirrus option,
    sys.argv = ["snek", "proj"]

    # when snek runs,
    run()

    # then cirrus files should not exist
    assert not path_exists("proj/.cirrus.yml")
