import snek


def test_version():
    version = snek.__version__.split(".")
    assert int(version[0]) >= 0


def test_unknown_version(version_raises_exception):
    version = snek.__version__
    assert version == "unknown"
