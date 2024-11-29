import copy
import pathlib
import pprint
import types

import pytest

from fspathtree import InvalidIndexError, NodeError, PathGoesAboveRoot, fspathtree


def test_accessing_non_existent_path():
    d = {
        "layers": [{"name": "abs1"}, {"name": "abs2"}],
        "grid": {"x": {"min": 0, "max": 1}, "y": {"min": 0, "max": 2}},
    }
    t = fspathtree(d)

    assert t["layers/0/name"] == "abs1"

    with pytest.raises(KeyError) as e:
        x = t["grid/0/x"]

    assert (
        e.value.args[0]
        == "Error while parsing path 'grid/0/x'. Could not find path element '0'."
    )

    with pytest.raises(InvalidIndexError) as e:
        x = t["layers/2/name"]

    assert (
        e.value.args[0]
        == "Error while parsing path 'layers/2/name'. '2' out of range for Sequence node index."
    )

    assert t["grid/x"]["../../layers/0/name"] == "abs1"

    with pytest.raises(KeyError) as e:
        assert t["grid/x"]["../layers/0/name"] == "abs1"

    assert (
        e.value.args[0]
        == "Error while parsing path '/grid/x/../layers/0/name'. Could not find path element 'layers'."
    )


def test_various_accessing_errors():

    d = {
        "layers": [{"name": "abs1"}, {"name": "abs2"}],
    }
    t = fspathtree(d)

    # missing (or mispelled) element
    with pytest.raises(KeyError) as e:
        assert t["layer/0/name"] == "abs1"
    assert (
        e.value.args[0]
        == "Error while parsing path 'layer/0/name'. Could not find path element 'layer'."
    )

    # indexing a list with non-integer (actually, non-number)
    with pytest.raises(ValueError) as e:
        assert t["layers/name"] == "abs1"
    assert (
        e.value.args[0]
        == "Error while parsing path 'layers/name'. Could not convert 'name' to an integer for indexing Sequence node."
    )

    # indexing a list with an index out of range
    with pytest.raises(InvalidIndexError) as e:
        assert t["layers/5/name"] == "abs1"
    assert (
        e.value.args[0]
        == "Error while parsing path 'layers/5/name'. '5' out of range for Sequence node index."
    )
