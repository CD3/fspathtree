# FS Path Tree

A simple class to allow filesystem-style path access to nested dict/list structures,
including support for walking "up" the tree with '..'.

Example:

```python
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
```

## API

The `fspathtree` class can be default constructed, with a `dict`, or with another `fspathtree`
```python
t1 = fspathtree()
t2 = fspathtree({'one':1})
t3 = fspathtree(t2)
```

Elements in the tree can be tested for presense using the `in` operator. They can be accessed with the
`__call__` operator or the `get(...)` method.
```
t = fspathtree({'one':{'two': 2}})

assert '/one/two' in t
assert t['/one/two'] == 2
assert '/one/three' not in t

t['/one/three'] = 3
assert '/one/three' in t
assert t['/one/three'] == 3

assert t.get('/one/three', None) == 3
assert t.get('/one/missing', None) is None
```
The `get_all_paths()` method returns a list of all paths in the tree (it actually returns a generator).
`get_all_leaf_node_paths()` returns a list of only leaf node paths. Both accept a predicate that can
be used to filer the paths that are returned.
```python
t = fspathtree({'one':{'two': 2}})

paths = list( t.get_all_paths() ) # returns [PathType('/'), PathType('/one'), PathType('two')]
paths = list( t.get_all_leafe_node_paths() ) # returns [PathType('two')]
paths = list( t.get_all_paths(predicate p: p.name == 'one') ) # returns [ PathType('/one')]

```


## Install

You can install the latest release with `pip`.
```
$ pip install fspathtree
```
Or, even better, using `pipenv`
```
$ pipenv install fspathtree
```
Or, even better better, using `poetry`
```
$ poetry add fspathtree
```

## Design

The `fspathtree` is a small wrapper class that can wrap any nested tree data structure. The tree that is wrapped can be accessed with
the `.tree` attribute. This is an improvement over the old `fspathdict.pdict` class, which stored nodes internally as `fspathdict.pdict` instances
and required "converting" to and from the standard python dict and list types.
