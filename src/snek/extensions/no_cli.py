"""
Extension that omits the creation of file `cli.py`
"""

from pathlib import PurePath as Path
from typing import List

from .. import structure
from ..actions import Action, ActionParams, ScaffoldOpts, Structure
from . import Extension


class NoSkeleton(Extension):
    """Omit creation of cli.py and test_cli.py"""

    def activate(self, actions: List[Action]) -> List[Action]:
        """Activate extension, see :obj:`~snek.extension.Extension.activate`."""
        return self.register(actions, remove_files, after="define_structure")


def remove_files(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Remove all cli files from structure

    Args:
        struct: project representation as (possibly) nested :obj:`dict`.
        opts: given options, see :obj:`create_project` for an extensive list.

    Returns:
        Updated project representation and options
    """
    # Namespace is not yet applied so deleting from package is enough
    src = Path("src")
    struct = structure.reject(struct, src / opts["package"] / "cli.py")
    struct = structure.reject(struct, "tests/test_cli.py")
    return struct, opts
