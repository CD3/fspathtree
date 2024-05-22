import pytest
import pprint
import types
import pathlib
import copy
from fspathtree import fspathtree, PathGoesAboveRoot, NodeError, InvalidIndexError


def test_finding_paths():
  d = {'one' : 1, 'level1' : {'two' : 2, 'nums' : [1,2,3], 'level3' : {'three' : 3}}, 'nums' : [1,2,3] }
  t = fspathtree(d)

  paths = list(t.get_all_leaf_node_paths())
  assert len(paths) == 9

  paths = list(t.get_all_paths())
  assert len(paths) == 14
  assert fspathtree.PathType("/") in paths
  assert fspathtree.PathType("/one") in paths
  assert fspathtree.PathType("/level1") in paths
  assert fspathtree.PathType("/level1/two") in paths
  assert fspathtree.PathType("/level1/nums") in paths
  assert fspathtree.PathType("/level1/nums/0") in paths
  assert fspathtree.PathType("/level1/nums/1") in paths
  assert fspathtree.PathType("/level1/nums/2") in paths
  assert fspathtree.PathType("/level1/level3") in paths
  assert fspathtree.PathType("/level1/level3/three") in paths
  assert fspathtree.PathType("/nums") in paths
  assert fspathtree.PathType("/nums/0") in paths
  assert fspathtree.PathType("/nums/1") in paths
  assert fspathtree.PathType("/nums/2") in paths

  paths = list(t.get_all_paths(transform=str))
  assert len(paths) == 14
  assert "/" in paths
  assert "/one" in paths
  assert "/level1" in paths
  assert "/level1/two" in paths
  assert "/level1/nums" in paths
  assert "/level1/nums/0" in paths
  assert "/level1/nums/1" in paths
  assert "/level1/nums/2" in paths
  assert "/level1/level3" in paths
  assert "/level1/level3/three" in paths
  assert "/nums" in paths
  assert "/nums/0" in paths
  assert "/nums/1" in paths
  assert "/nums/2" in paths

  paths = list(t.get_all_paths(transform=str,predicate= lambda p, n: fspathtree.is_leaf(n)))
  assert len(paths) == 9
  assert "/" not in paths
  assert "/one" in paths
  assert "/level1" not in paths
  assert "/level1/two" in paths
  assert "/level1/nums" not in paths
  assert "/level1/nums/0" in paths
  assert "/level1/nums/1" in paths
  assert "/level1/nums/2" in paths
  assert "/level1/level3" not in paths
  assert "/level1/level3/three" in paths
  assert "/nums" not in paths
  assert "/nums/0" in paths
  assert "/nums/1" in paths
  assert "/nums/2" in paths



  paths = list(t.get_all_paths(predicate = lambda p: p.name == 'level3' ))
  assert len(paths) == 1
  assert 'three' in t[paths[0]]
  assert t[paths[0]]['three'] == 3


  paths = list(t.get_all_leaf_node_paths(predicate = lambda p: p.name == 'three' ))
  assert len(paths) == 1

  paths = list(t.get_all_leaf_node_paths(predicate = lambda p: p.name == 'level3' ))
  assert len(paths) == 0


  paths = list(t.get_all_paths(predicate = lambda p: p.name == 'three' ))
  assert len(paths) == 1

  paths = list(t.get_all_paths(predicate = lambda p: p.name == 'level3' ))
  assert len(paths) == 1
