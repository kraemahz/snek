from pathlib import Path
from shutil import copytree

import pytest

from snek import cli
from snek import file_system as fs
from snek import shell
from snek.exceptions import ExtensionNotFound


def copy_example(name, target_dir) -> Path:
    example = Path(__file__).parent / "examples" / name
    target = Path(target_dir, name)
    return Path(copytree(str(example), str(target)))


def test_issue506(tmpfolder):
    try:
        # Given a project exists with the same `setup.cfg` from issue506
        with fs.chdir(copy_example("issue-506", tmpfolder)):
            shell.git("init", ".")
            shell.git("add", ".")
            shell.git("commit", "-m", "Add code before update")
            # when we run the update
            cli.main([".", "--update", "--force"])
            # then no error should be raised when updating
            # and the extension should load correctly (e.g. namespace)
            assert Path("src/snekext/company/__init__.py").exists()
            assert not Path("src/snekext/__init__.py").exists()
            assert not Path("src/company").exists()
    except ExtensionNotFound as ex:
        pytest.skip(f"Test cannot succeed without extensions.\n{ex}")
