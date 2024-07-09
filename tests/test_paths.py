import pytest
import pathlib
import copy
from fspathtree import fspathtree


def test_get_nodes_path():
    d = {
        "one": 1,
        "level1": {"two": 2, "nums": [1, 2, 3], "level3": {"three": 3}},
        "nums": [1, 2, 3],
    }
    t = fspathtree(d)

    x = t["/level1/level3"]

    assert type(x.path()) == pathlib.PurePosixPath
    assert str(x.path()) == "/level1/level3"
    assert x.path() == pathlib.PurePosixPath("/level1/level3")


def test_path_normalization():

    assert str(fspathtree.normalize_path("/one/two")) == "/one/two"
    assert str(fspathtree.normalize_path("/one/two/./")) == "/one/two"
    assert str(fspathtree.normalize_path("/one/./two/")) == "/one/two"
    assert str(fspathtree.normalize_path("/one/../two/")) == "/two"
    assert str(fspathtree.normalize_path("/one/two/three/../four")) == "/one/two/four"
    assert str(fspathtree.normalize_path("/one/two/three/../../four")) == "/one/four"
