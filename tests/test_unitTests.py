import pytest
import pprint
import types
import pathlib
import copy
from fspathtree import fspathtree, PathGoesAboveRoot, NodeError, InvalidIndexError

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

  assert type(d['level1']['nums']) == list
  assert type(t['/level1/nums']) == fspathtree
  assert type(t['/level1/nums'].tree) == list

  assert t["/level1/nums/0"] == 1
  assert t["/level1/nums/1"] == 2
  assert t["/level1/nums/2"] == 3

  keys = list(t.get_all_leaf_node_paths())
  assert len(keys) == 9
  assert type(keys[0]) == pathlib.PurePosixPath

  # add some keys
  d['three'] = 3
  assert t['three'] == 3

  t['/four'] = 4
  assert d['four'] == 4

  t['/level1/level2/level3/level4'] = [10,20]
  assert type(d['level1']['level2']['level3']['level4']) == list
  assert type(t['level1/level2/level3/level4']) == fspathtree
  assert t['level1/level2/level3/level4/0'] == 10
  assert t['level1/level2/level3/level4/1'] == 20




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

def test_fspathtree_adding_to_nested_dict():
  d = {'items' : [ {'x' : 1, 'y' : 2}, {'x' : "one",'y' : "two"} ] }

  t =  fspathtree(d)
  t['/items/2/x'] = 3


  assert len(t['/items'].tree) == 3
  assert t['/items/0/x'] == 1
  assert t['/items/1/x'] == "one"
  assert t['/items/2/x'] == 3
  assert t['/items/0/y'] == 2
  assert t['/items/1/y'] == "two"

  t['items/5/z'] = "six"
  assert len(t['/items'].tree) == 6
  assert t['/items/3'] is None
  assert t['/items/4'] is None
  assert t['/items/5/z'] == "six"

  t['items/0/x'] = "one"
  assert len(t['/items'].tree) == 6
  assert t['/items/0/x'] == "one"

  assert type(t.tree['items']) == list





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
  paths = list(paths)
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

  paths = d.get_all_leaf_node_paths(transform=str)
  paths = list(paths)
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

def test_static_methods():

  d = { 'one' : 1, 'l2' : { 'one' : 1, 'two' : 2, 'l3' : {'one' : 1 } } }

  assert fspathtree.getitem( d, 'one' ) == 1
  assert fspathtree.getitem( d, '/one' ) == 1

  fspathtree.setitem(d, "two", 2);
  fspathtree.setitem(d, "l2/l3/l4/l5/one", 10);

  assert fspathtree.getitem( d, '/two' ) == 2
  assert fspathtree.getitem( d, '/l2/l3/l4/l5/one' ) == 10

def test_searching():
  t = fspathtree( { 'one' : 1, 'l2' : { 'one' : 1, 'two' : 2, 'l3' : {'one' : 1 } }, 'll2' : {'one' : 11}  } )

  assert t._make_path('/one').match("one")
  assert not t._make_path('/l2/one').match("/one")
  assert t._make_path('/l2/one').match("one")
  assert t._make_path('l2/one').match("one")
  assert not t._make_path('l2/one').match("/one")
  assert t._make_path('/l2/one').match("*/one")
  assert not t._make_path('/l2/l3/one').match("/*/one")
  assert t._make_path('/l2/l3/one').match("*/one")
  assert t._make_path('/l2/l3/one').match("l3/one")
  assert not t._make_path('/l2/l3/one').match("l4/one")

  keys = t.find("/one")
  assert isinstance( keys, types.GeneratorType )

  keys = list(t.find("/one"))
  assert len(keys) == 1

  keys = list(t.find("one"))
  assert len(keys) == 4

  keys = list(t.find("l2/*"))
  assert len(keys) == 2

  keys = list(t.find("l*/one"))
  assert len(keys) == 3

def test_new_instances_are_empty():
  t = fspathtree({'one':1})

  assert len(t.tree) == 1

  t = fspathtree()

  assert len(t.tree) == 0


def test_searching_predicates():
  t = fspathtree()

  t['/l11/l12/l13/one'] = 1
  t['/l11/l12/l13/two'] = 2
  t['/l21/l12/l13/two'] = 2
  t['/l21/l12/l23/two'] = 2
  t['/l21/l12/l23/three'] = 3
  t['/l21/l12/l23/four'] = "4"

  keys = t.get_all_leaf_node_paths()
  assert isinstance( keys, types.GeneratorType )

  keys = list(t.get_all_leaf_node_paths())
  assert len(keys) == 6

  keys = list(t.get_all_leaf_node_paths(predicate = lambda x : str(x).endswith("r")))
  assert len(keys) == 1

  keys = list(t.get_all_leaf_node_paths(predicate = lambda x,y : type(y) == str))
  assert len(keys) == 1
  assert fspathtree.PathType("/l21/l12/l23/four") in keys

  keys = list(t.get_all_leaf_node_paths(predicate = lambda x,y : type(y) is int and y < 3))
  assert len(keys) == 4
  assert fspathtree.PathType("/l11/l12/l13/one") in keys


def test_searching_transforms():
  t = fspathtree()

  t['/l11/l12/l13/one'] = 1
  t['/l11/l12/l13/two'] = 2
  t['/l21/l12/l13/two'] = 2
  t['/l21/l12/l23/two'] = 2
  t['/l21/l12/l23/three'] = 3
  t['/l21/l12/l23/four'] = "4"

  items = list(t.get_all_leaf_node_paths(transform = lambda k,v: (str(k),v) ))
  assert len(items) == 6
  assert type(items[0]) == tuple

  items = t.get_all_leaf_node_paths(transform = lambda k,v: (str(k),v) )
  assert type(next(items)) == tuple


def test_missing_key_errors():
  t = fspathtree()

  t['/l11/l12/l13/one'] = 1

  with pytest.raises(KeyError,match=r".*'l12'.*"):
    t['l12']


def test_updating_multi_level_trees():

    t = fspathtree()
    t['/l1/l2/l3/val1'] = 'one'
    t['/l1/l2/l3/val2'] = 'two'
    t['/l1/l2/l3/items'] = ['three','four']

    assert t['/l1/l2/l3/val1'] == 'one'
    assert t['/l1/l2/l3/val2'] == 'two'
    assert t['/l1/l2/l3/items/0'] == 'three'
    assert t['/l1/l2/l3/items/1'] == 'four'

    t2 = fspathtree()
    t2['/l1/l2/l3/items'] = ['five','six']

    t.update(t2)

    assert t['/l1/l2/l3/val1'] == 'one'
    assert t['/l1/l2/l3/val2'] == 'two'
    assert t['/l1/l2/l3/items/0'] == 'five'
    assert t['/l1/l2/l3/items/1'] == 'six'

    t2['/l1/l2/l3/items/0'] = 'seven'
    t2['/l1/l2/l3/items/2'] = 'eight'

    assert type(t2['/l1/l2/l3/items'].tree) == list
    assert len(t2['/l1/l2/l3/items'].tree) == 3

    d = { 'l1' : { 'l2' : {'val1' : 'nine' }, 'items' : [0,1,2]} }


    t.update(t2,d,var1='val1')

    assert t['/l1/l2/val1'] == "nine"
    assert t['/l1/items/0'] == 0
    assert t['/l1/items/1'] == 1
    assert t['/l1/items/2'] == 2
    assert t['/l1/l2/l3/val1'] == "one"
    assert t['/l1/l2/l3/items/0'] == "seven"
    assert t['/l1/l2/l3/items/1'] == "six"
    assert t['/l1/l2/l3/items/2'] == "eight"
    assert t['/var1'] == "val1"


    t2['/l1/l2/l3/items/10'] = '10'
    assert type(t2['/l1/l2/l3/items'].tree) == list
    assert len(t2['/l1/l2/l3/items'].tree) == 11
    assert t2['/l1/l2/l3/items'].tree[0] == "seven"
    assert t2['/l1/l2/l3/items'].tree[1] == "six"
    assert t2['/l1/l2/l3/items'].tree[2] == "eight"
    assert t2['/l1/l2/l3/items'].tree[3] == None
    assert t2['/l1/l2/l3/items'].tree[10] == "10"



    # check that we can derive from fspathtree and this still works
    class my_fspathtree(fspathtree):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)


    t1 = my_fspathtree({'k1':'v1'})
    t2 = my_fspathtree( {'k2':'v2', 'l1' : {'k1':'v1'}})

    assert 'l1/k1' not in t1
    assert t2['l1/k1'] == 'v1'

    assert isinstance(t1,my_fspathtree)
    assert isinstance(t1,fspathtree)

    t1.update(t2)

    assert 'l1/k1' in t1
    assert t1['l1/k1'] == 'v1'
    assert t2['l1/k1'] == 'v1'

    class MyType:
        pass

    t1 = my_fspathtree({'l1' : {'k1':MyType()}})
    t2 = my_fspathtree({'l1' : {'k1':['1','2']}})

    assert type(t1['/l1/k1']) == MyType

    t1.update(t2)

    assert t1['/l1/k1/0'] == '1'
    assert t1['/l1/k1/1'] == '2'
    assert type(t1['/l1/k1'].tree) == list





def test_accessing_and_creating_paths_deeper_than_leaf_nodes():
    # We can easily create nested structures by just setting elements
    # with a nested path. The parents will be created automatically.
    t1 = fspathtree()
    t1['l1/l2/l3/v1'] = 1
    assert t1['l1/l2/l3/v1'] == 1

    # We can change the volue of any *existing* non-leaf note easily too.
    t1['l1/l2/l3'] = 1
    assert t1['l1/l2/l3'] == 1

    t1['l1/l2/l3'] = [0,1]
    assert t1['l1/l2/l3/0'] == 0
    assert t1['l1/l2/l3/1'] == 1
    assert type(t1['l1/l2/l3'].tree) == list
    assert type(t1['l1/l2'].tree) == dict

    # If we try to access elements of non-leaf nodes that don't
    # exist, we should get a Key error
    with pytest.raises(Exception) as e_info:
        t1['l2']
    assert e_info.type == KeyError
    assert str(e_info.value).strip('"') == "Could not find path element 'l2' while parsing path 'l2'"

    with pytest.raises(Exception) as e_info:
        t1['l1/l3/l3']
    assert e_info.type == KeyError
    assert str(e_info.value).strip('"') == "Could not find path element 'l3' while parsing path 'l1/l3/l3'"

    with pytest.raises(Exception) as e_info:
        t1['l1/l2/l2']
    assert e_info.type == KeyError
    assert str(e_info.value).strip('"') == "Could not find path element 'l2' while parsing path 'l1/l2/l2'"

    # Or an index error for lists
    with pytest.raises(Exception) as e_info:
        t1['l1/l2/l3/2']
    assert e_info.type == IndexError
    assert str(e_info.value).strip('"') == "Could not find path element '2' while parsing path 'l1/l2/l3/2'"


    t1['l1/l2'] = None
    with pytest.raises(Exception) as e_info:
        t1['l1/l2/l3']
    assert e_info.type == NodeError
    assert str(e_info.value).strip('"') == "Unknown parent node type (<class 'NoneType'>) found at 'l1/l2' while traversing path 'l1/l2/l3'. This likely means you are trying to access an element beyond a current leaf node."

    t1['l1/l2'] = 1
    with pytest.raises(Exception) as e_info:
        t1['l1/l2/l3']
    assert e_info.type == NodeError
    assert str(e_info.value).strip('"') == "Unknown parent node type (<class 'int'>) found at 'l1/l2' while traversing path 'l1/l2/l3'. This likely means you are trying to access an element beyond a current leaf node."


    t1['l1/l2/l3'] = 2
    assert type(t1['l1/l2'].tree) == dict
    assert type(t1['l1/l2/l3']) == int
    assert t1['l1/l2/l3'] == 2


    t1['l1/l2/l3/1'] = 3
    assert type(t1['l1/l2/l3'].tree) == list
    assert t1['l1/l2/l3/0'] == None
    assert t1['l1/l2/l3/1'] == 3



def test_using_list_and_dict_nodes():
    t1 = fspathtree()


    t1['l1/l2'] = [1,2]

    assert type(t1['/l1/l2'].tree) == list
    assert type(t1['/l1/l2/0']) == int
    assert type(t1['/l1/l2/1']) == int
    assert t1['/l1/l2/0'] == 1
    assert t1['/l1/l2/1'] == 2

    with pytest.raises(Exception) as e_info:
        t1['/l1/l2/val'] = 3
    assert e_info.type == IndexError
    assert str(e_info.value).strip('"') == "Error while parsing path '/l1/l2/val'. Non-numeric index 'val' used to index Sequence node."

    assert '/l1/l2' in t1
    assert '/l1/l2/0' in t1
    assert '/l1/l2/1' in t1
    assert '/l1/l2/val' not in t1


    t1 = fspathtree([1,2])
    assert type(t1.tree) == list
    assert t1['/0'] == 1
    assert t1['/1'] == 2

    with pytest.raises(Exception) as e_info:
        t1['/val'] = 3
    assert e_info.type == IndexError
    assert str(e_info.value).strip('"') == "Error while parsing path '/val'. Non-numeric index 'val' used to index Sequence node."

    assert type(t1.tree) == list
    assert t1['/0'] == 1
    assert t1['/1'] == 2

    t1 = fspathtree()
    t1['l1/l2/0'] = 1
    t1['l1/l2/1'] = 2

    assert type(t1['/l1/l2'].tree) == list
    assert type(t1['/l1/l2/0']) == int
    assert type(t1['/l1/l2/1']) == int
    assert t1['/l1/l2/0'] == 1
    assert t1['/l1/l2/1'] == 2

    t1 = fspathtree()
    t1['l1/l2/0/0'] = 1
    t1['l1/l2/0/1'] = 2
    t1['l1/l2/1/0'] = 3
    t1['l1/l2/1/1'] = 4

    assert type(t1['/l1/l2'].tree) == list
    assert type(t1['/l1/l2/0'].tree) == list
    assert type(t1['/l1/l2/1'].tree) == list
    assert t1['/l1/l2/0'].tree == [1,2]
    assert t1['/l1/l2/1'].tree == [3,4]






def test_constructors():
    d = {'k1':'v1'}

    t = fspathtree(d)
    assert type(t.tree) == dict

    t2 = fspathtree(t)
    assert type(t2.tree) == dict

    t2['/k2'] = 'v2'

    assert len(d) == 2
    assert d['k2'] == 'v2'

    t3 = fspathtree(copy.deepcopy(t))

    t3['/k3'] = 'v3'

    assert len(d) == 2
    assert d['k2'] == 'v2'


    assert len(t3.tree) == 3
    assert t3.tree['k1'] == 'v1'
    assert t3.tree['k2'] == 'v2'
    assert t3.tree['k3'] == 'v3'


    # check that we can derive from fspathtree and this still works
    class my_fspathtree(fspathtree):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)


    d = {'k1':'v1'}

    t = my_fspathtree(d)
    assert type(t.tree) == dict

    t2 = my_fspathtree(t)
    assert type(t2.tree) == dict

def test_getting_leaf_nodes():
  d = {'one' : 1, 'level1' : {'two' : 2, 'nums' : [1,2,3],'level3' : {'three' : 3}}, 'nums' : [1,2,3] }
  t = fspathtree(d)


  keys = list(t.get_all_leaf_node_paths())

  assert len(keys) == 9
  assert keys[0] in t
  assert keys[1] in t
  assert keys[2] in t

  assert fspathtree.PathType("/one") in keys
  assert fspathtree.PathType("/level1/two") in keys

  keys = list(t['level1'].get_all_leaf_node_paths())


  assert len(keys) == 5
  assert keys[0] in t['level1']
  assert keys[1] in t['level1']
  assert keys[2] in t['level1']

  assert fspathtree.PathType("two") in keys
  assert fspathtree.PathType("nums/0") in keys

