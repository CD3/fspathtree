import pytest
import pathlib
import copy
from fspathtree import fspathtree


def test_update_with_dict():
    d = {
        "one": 1,
        "level1": {"two": 2, "nums": [1, 2, 3], "level3": {"three": 3}},
        "nums": [1, 2, 3],
    }
    t = fspathtree(d)

    assert "/one" in t
    assert "/level1/two" in t
    assert "/level1/nums/0" in t

    assert t["/one"] == 1
    assert t["/level1/two"] == 2
    assert t["/level1/nums/0"] == 1

    t.update({"level1": {"two": 4}})

    assert "/one" in t
    assert "/level1/two" in t
    assert "/level1/nums/0" not in t

    assert t["/one"] == 1
    assert t["/level1/two"] == 4


def test_update_with_dict():
    d = {
        "one": 1,
        "level1": {"two": 2, "nums": [1, 2, 3], "level3": {"three": 3}},
        "nums": [1, 2, 3],
    }
    t = fspathtree(d)

    assert "/one" in t
    assert "/level1/two" in t
    assert "/level1/nums/0" in t

    assert t["/one"] == 1
    assert t["/level1/two"] == 2
    assert t["/level1/nums/0"] == 1

    t.update(fspathtree({"level1": {"two": 4}}))

    assert "/one" in t
    assert "/level1/two" in t
    assert "/level1/nums/0" in t

    assert t["/one"] == 1
    assert t["/level1/two"] == 4
    assert t["/level1/nums/0"] == 1
