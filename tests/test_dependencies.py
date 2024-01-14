import sys

import pytest

from snek import dependencies as deps


@pytest.mark.skipif(
    sys.version_info[:2] <= (3, 7),
    reason="regex doesn't work well in py36 (for some edge cases)",
)
def test_split():
    assert deps.split(
        "\n    snek>=42.1.0,<43.0"
        "\n    platformdirs==1"
        "\n    cookiecutter<8"
        "\n    mypkg~=9.0"
    ) == ["snek>=42.1.0,<43.0", "platformdirs==1", "cookiecutter<8", "mypkg~=9.0"]
    assert deps.split(
        "\n    snek>=42.1.0,<43.0;platformdirs==1"
        "\n    cookiecutter<8;mypkg~=9.0\n\n"
    ) == ["snek>=42.1.0,<43.0", "platformdirs==1", "cookiecutter<8", "mypkg~=9.0"]
    assert deps.split(
        "snek>=42.1.0,<43.0; platformdirs==1; cookiecutter<8; mypkg~=9.0; "
    ) == ["snek>=42.1.0,<43.0", "platformdirs==1", "cookiecutter<8", "mypkg~=9.0"]
    assert deps.split(
        "\n    snek>=42.1.0,<43.0;python_version>='3.4'; platformdirs==1"
    ) == ["snek>=42.1.0,<43.0;python_version>='3.4'", "platformdirs==1"]
    assert deps.split(
        "\n    snek>=42.1.0,<43.0; python_version>='3.4'; platformdirs==1"
    ) == ["snek>=42.1.0,<43.0; python_version>='3.4'", "platformdirs==1"]


def test_deduplicate():
    # no duplication => no effect
    assert deps.deduplicate(["snek>=4,<5", "platformdirs"]) == [
        "snek>=4,<5",
        "platformdirs",
    ]
    # duplicated => the last one wins
    assert deps.deduplicate(
        ["snek>=4,<5", "snek~=3.2", "snek==0"]
    ) == ["snek==0"]
    assert deps.deduplicate(
        ["snek==0", "snek>=4,<5", "snek~=3.2"]
    ) == ["snek~=3.2"]


def test_remove():
    assert deps.remove(
        ["snek>=42.1.0,<43.0", "platformdirs==1", "cookiecutter<8", "mypkg~=9.0"],
        ["platformdirs"],
    ) == ["snek>=42.1.0,<43.0", "cookiecutter<8", "mypkg~=9.0"]
    assert deps.remove(
        ["snek>=42.1.0,<43.0", "platformdirs==1", "cookiecutter<8", "mypkg~=9.0"],
        {"mypkg": 0},
    ) == ["snek>=42.1.0,<43.0", "platformdirs==1", "cookiecutter<8"]


def test_add():
    own_deps = [
        "setuptools_scm>=1.2.5,<2",
        "snek>=42.1.0,<43",
        "django>=5.3.99999,<6",
    ]
    # No intersection
    assert deps.add(["platformdirs==1", "cookiecutter<8", "mypkg~=9.0"], own_deps) == [
        "platformdirs==1",
        "cookiecutter<8",
        "mypkg~=9.0",
        "setuptools_scm>=1.2.5,<2",
        "snek>=42.1.0,<43",
        "django>=5.3.99999,<6",
    ]
    # With intersection => own_deps win
    assert deps.add(["platformdirs==1", "snek<8", "mypkg~=9.0"], own_deps) == [
        "platformdirs==1",
        "snek>=42.1.0,<43",
        "mypkg~=9.0",
        "setuptools_scm>=1.2.5,<2",
        "django>=5.3.99999,<6",
    ]


def test_add_commented():
    new_deps = [
        "setuptools_scm>=1.2.5,<2",
        "snek>=42.1.0,<43",
        "django>=5.3.99999,<6",
        "mypkg~=9.0",
        "gitdep @ git+https://repo.com/gitdep@main#egg=gitdep",
        "# a comment",
        "# comment-that>0==1<3; reminds.pep==508",
    ]
    assert deps.add(["platformdirs==1", "# a comment", "# mypkg~=2.0"], new_deps) == [
        "platformdirs==1",
        "# a comment",
        "mypkg~=9.0",
        "setuptools_scm>=1.2.5,<2",
        "snek>=42.1.0,<43",
        "django>=5.3.99999,<6",
        "gitdep @ git+https://repo.com/gitdep@main#egg=gitdep",
        "# comment-that>0==1<3; reminds.pep==508",
    ]
