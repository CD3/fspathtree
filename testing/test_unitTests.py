import pytest,pprint
from fspathtree import fspathtree, PathGoesAboveRoot

def test_fspathtree_wrapping_existing_dict():
  d = {'one' : 1, 'level1' : {'two' : 2, 'nums' : [1,2,3],'level3' : {'three' : 3}}, 'nums' : [1,2,3] }

  t = fspathtree(d)

  assert t['one'] == 1
  assert t['level1/two'] == 2
  assert t['level1']['two'] == 2
  assert t['level1']['level3/three'] == 3
  assert t['level1']['level3/../two'] == 2
  with pytest.raises(PathGoesAboveRoot):
    assert t['../'] == 1
  assert t['level1']['../one'] == 1
  with pytest.raises(PathGoesAboveRoot):
    assert t['level1']['../../one'] == 1
  assert t['level1']['/one'] == 1
  assert t['level1/level3']['../../one'] == 1
  assert t['level1/level3']['/one'] == 1
  assert t['level1/level3']['//one'] == 1

  assert t.tree['one'] == 1
  assert type(t.tree) == dict

  d['three'] = 3
  assert t['three'] == 3

def test_fspathtree_creating_nested_dict():
  t = fspathtree()

  t['/level1/level2/level3/one'] = 1
  assert t.tree['level1']['level2']['level3']['one'] == 1
  assert len(t.tree) == 1
  assert len(t.tree.keys()) == 1

  t['/level1/level2/level3/level4/'] = dict()
  assert type(t.tree['level1']['level2']['level3']['level4']) == dict

  l2 = t['/level1/level2']

  l2['one'] = 1
  l2['/one'] = 1
  l2['../two'] = 2

  assert t.tree['level1']['level2']['one'] == 1
  assert t.tree['one'] == 1
  assert t.tree['level1']['two'] == 2

def test_fspathtree_wrapping_existing_list():
  d = ['one', 'two', 'three']
  t = fspathtree(d)

  assert t['0'] == "one"

def test_interface():
  d = fspathtree()

  d['type'] = 'plain'
  d['grid'] = dict()
  d['grid']['dimensions'] = 2
  d['grid']['x'] = dict()
  d['grid']['x']['min'] = 0
  d['grid']['x']['max'] = 2.5
  d['grid']['x']['n'] = 100
  d['grid']['y'] = { 'min' : -1, 'max' : 1, 'n' : 200 }
  d['time'] = { 'stepper' : { 'type' : 'uniform', 'tolerance' : {'min' : 1e-5, 'max' : 1e-4} } }
  d['search'] = { 'method' : 'bisection', 'range' : [0, 100] }
  d['sources'] = [ {'type' : 'laser'}, {'type' : 'RF' } ]


  assert d['type'] == "plain"
  assert d['grid']['dimensions'] == 2
  assert d['grid']['x']['min'] == 0
  assert d['grid']['x']['max'] == 2.5
  assert d['grid']['x']['n'] == 100
  assert d['grid']['y']['min'] == -1
  assert d['grid']['y']['max'] == 1
  assert d['grid']['y']['n'] == 200
  assert d['time']['stepper']['type'] == "uniform"
  assert d['time']['stepper']['tolerance']['min'] == 1e-5
  assert d['time']['stepper']['tolerance']['max'] == 1e-4
  assert d['search']['method'] == 'bisection'
  assert d['search']['range'][0] == 0
  assert d['search']['range']['1'] == 100
  assert d['sources'][0]['type'] == 'laser'
  assert d['sources'][1]['type'] == 'RF'

  assert d['type'] == "plain"
  assert d['grid/dimensions'] == 2
  assert d['grid/x/min'] == 0
  assert d['grid/x/max'] == 2.5
  assert d['grid/x/n'] == 100
  assert d['grid/y/min'] == -1
  assert d['grid/y/max'] == 1
  assert d['grid/y/n'] == 200
  assert d['time/stepper/type'] == "uniform"
  assert d['time/stepper/tolerance/min'] == 1e-5
  assert d['time/stepper/tolerance/max'] == 1e-4
  assert d['search/method'] == 'bisection'
  assert d['search/range/0'] == 0
  assert d['search/range/1'] == 100
  assert d['sources/0/type'] == 'laser'
  assert d['sources/1/type'] == 'RF'

  assert d['grid/x/min'] == 0
  assert d['grid/x/max'] == 2.5
  assert d['grid/x/n'] == 100

  assert d['grid/x']['../dimensions'] == 2

  assert d['grid/x']['../y/min'] == -1
  assert d['grid/x']['../y/max'] == 1
  assert d['grid/x']['../y/n'] == 200
  assert d['grid/x']['/type'] == "plain"
  assert d['grid/x']['/grid/y/min'] == -1
  assert d['grid/x']['/grid/y/max'] == 1
  assert d['grid/x']['/grid/y/n'] == 200

  d = fspathtree()
  d.tree.update( {'grid' : { 'x' : { 'min' : 0, 'max' : 1, 'n' : 100 } } } )

  assert d['grid']['x']['min'] == 0
  assert d['grid']['x']['max'] == 1
  assert d['grid']['x']['n'] == 100

  assert d['grid/x/min'] == 0
  assert d['grid/x/max'] == 1
  assert d['grid/x/n'] == 100

  d = fspathtree()
  d['grid/x/min'] = 0
  d['grid/x']['max'] = 1
  d['grid/x']['/grid/x/n'] = 100
  d['grid/x']['/type'] = "sim"

  assert d['grid']['x']['min'] == 0
  assert d['grid']['x']['max'] == 1
  assert d['grid']['x']['n'] == 100
  assert d['type'] == 'sim'


def test_dict_conversions():
  d = fspathtree( { 'a' : { 'b' : { 'c' : { 'd' : 0 }, 'e' : [ 0, 1, 2, [10, 11, 12] ] } } } )

  assert d['a/b/c/d'] == 0
  assert d['a/b/e/0'] == 0
  assert d['a/b/e/1'] == 1

  assert d['a/b/c/d'] == 0
  assert d['a/b/e/0'] == 0
  assert d['a/b/e/1'] == 1
  assert d['a/b/e/2'] == 2
  assert d['a/b/e/3/0'] == 10
  assert d['a/b/e/3/1'] == 11
  assert d['a/b/e/3/2'] == 12

  assert d['a/b/e/2'] == 2
  assert d['a/b/e/3/0'] == 10

  assert type(d) == fspathtree
  assert type(d['a']) == fspathtree
  assert type(d['a/b']) == fspathtree
  assert type(d['a/b/c']) == fspathtree
  assert type(d['a/b/c/d']) == int
  assert type(d['a/b/e']) == fspathtree
  assert type(d['a/b/e/0']) == int
  assert type(d['a/b/e/3']) == fspathtree
  assert type(d['a/b/e/3/0']) == int

  dd = d.tree

  assert dd['a']['b']['c']['d'] == 0
  assert dd['a']['b']['e'][0] == 0
  assert dd['a']['b']['e'][1] == 1
  assert dd['a']['b']['e'][2] == 2
  assert dd['a']['b']['e'][3][0] == 10

  assert type(dd) == dict
  assert type(dd['a']) == dict
  assert type(dd['a']['b']) == dict
  assert type(dd['a']['b']['c']) == dict
  assert type(dd['a']['b']['c']['d']) == int
  assert type(dd['a']['b']['e']) == list
  assert type(dd['a']['b']['e'][0]) == int
  assert type(dd['a']['b']['e'][3]) == list
  assert type(dd['a']['b']['e'][3][0]) == int


def test_paths():
  d = fspathtree()

  d.update( { 'type':'sim', 'grid' : { 'x' : { 'min' : 0, 'max' : 10, 'n' : 100 } } } )

  assert str(d['grid']['x'].path()) == '/grid/x'
  assert str(d['grid']['x']['..'].path()) == '/grid'
  assert str(d['grid']['x']['../'].path()) == '/grid'
  assert str(d['grid']['x']['../../grid'].path()) == '/grid'

  # assert d['grid']['/.'] == d
  # assert d['grid']['/'] == d

  assert str(d["grid/x"].path().parent) == '/grid'
  assert str(d["/grid/x"].path().parent) == '/grid'

  assert str(d["grid/x"].path().stem) == 'x'
  assert str(d["/grid/x"].path().stem) == 'x'

def test_readme_example():
  config = fspathtree()
  config.update( { 'desc' : "example config"
                 , 'time' : { 'N' : 50
                            , 'dt' : 0.01 }
                 , 'grid' : { 'x' : { 'min' : 0
                                    , 'max' : 0.5
                                    , 'N' : 100 }
                            , 'y' : { 'min' : 1
                                    , 'max' : 1.5
                                    , 'N' : 200 }
                            }
                 } )

  # elements are accessed in the same was as a dict.
  assert config['desc'] == "example config"
  # sub-elements can also be accessed the same way.
  assert config['grid']['x']['max'] == 0.5
  # but they can also be accessed using a path.
  assert config['grid/x/max'] == 0.5

  # get a sub-element in the tree.
  x = config['grid/x']

  # again, elements of grid/x are accessed as normal.
  assert x['max'] == 0.5
  # but we can also access elements that are not in this branch.
  assert x['../y/max'] == 1.5
  # or reference elements from the root of the tree.
  assert x['/time/N'] == 50

  
def test_get_method():
  d = fspathtree()
  d.update({ 'one': 1,
        'level 1' : {'one' : 11, 'two': 12} })


  assert d['one'] == 1
  assert d['level 1/one'] == 11
  assert d['level 1/two'] == 12

  with pytest.raises(KeyError) as e:
    x = d['two']

  with pytest.raises(KeyError) as e:
    x = d['level 1/three']

  with pytest.raises(KeyError) as e:
    x = d['level 2']

  with pytest.raises(KeyError) as e:
    x = d['level 2/one']

  assert d.get('one',-1) == 1
  assert d.get('level 1/one',-1) == 11
  assert d.get('level 1/two',-1) == 12

  assert d.get('two',-1) == -1
  assert d.get('level 2',-1) == -1
  assert d.get('level 2/one',-1) == -1


def test_construct_from_dict():
  d = fspathtree({ 'one': 1,
        'level 1' : {'one' : 11, 'two': 12} })

  assert d['one'] == 1
  assert d['level 1/one'] == 11
  assert d['level 1/two'] == 12


def test_get_all_leaf_node_paths():
  d = fspathtree( {'one' : 1, 'level1' : {'two' : 2, 'nums' : [1,2,3],'level2' : {'three' : 3, 'nums' : [1,2,3] } } } )

  paths = d.get_all_leaf_node_paths()
  assert len(paths) == 9
  assert d.PathType("/one") in paths
  assert d.PathType("/level1/two") in paths
  assert d.PathType("/level1/nums/0") in paths
  assert d.PathType("/level1/nums/1") in paths
  assert d.PathType("/level1/nums/2") in paths
  assert d.PathType("/level1/level2/three") in paths
  assert d.PathType("/level1/level2/nums/0") in paths
  assert d.PathType("/level1/level2/nums/1") in paths
  assert d.PathType("/level1/level2/nums/2") in paths

  paths = d.get_all_leaf_node_paths(as_str=True)
  assert len(paths) == 9
  assert "/one" in paths
  assert "/level1/two" in paths
  assert "/level1/nums/0" in paths
  assert "/level1/nums/1" in paths
  assert "/level1/nums/2" in paths
  assert "/level1/level2/three" in paths
  assert "/level1/level2/nums/0" in paths
  assert "/level1/level2/nums/1" in paths
  assert "/level1/level2/nums/2" in paths
