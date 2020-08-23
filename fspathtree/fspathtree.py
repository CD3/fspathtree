from pathlib import PurePosixPath
import re

class PathGoesAboveRoot(Exception):
  pass

class fspathtree:
  """A small class that wraps a tree data struction and allow accessing the nested elements using filesystem-style paths."""
  DefaultNodeType = dict
  PathType = PurePosixPath
  IndexableLeafTypes = [str,bytes]

  def __init__(self,tree=DefaultNodeType(),root=None,abspath='/'):
    self.tree = tree
    self.root = root if root is not None else tree

    self.abspath = self.PathType(abspath)
    
    if self.tree == self.root and abspath != '/':
      raise RuntimeError("fspathtree: tree initialized with a root, but abspath is not '/'.")

    if self.tree != self.root and abspath == '/':
      raise RuntimeError("fspathtree: tree initialized with an abspath '/', but the tree and root are not the same.")

    self.get_all_leaf_node_paths = self._instance_get_all_leaf_node_paths

  @staticmethod
  def make_path(key):
    '''
    Given a string, bytes array, or integer;  return a PathType object representing the path.
    '''
    if type(key) in (list,tuple):
      key = '/'.join(key)

    if type(key) in (str,bytes):
      key = re.sub(r'^\/+','/',key) # replace multiple '/' at front with a single '/'. i.e. // -> /

    if type(key) in (int,):
      key = str(key)

    path = fspathtree.PathType(key)

    return path


  def __getitem__(self,key):
    path = self.make_path(key)

    if path.is_absolute():
      item = fspathtree.getitem(self.root,path.relative_to('/'))
      if type(item) not in fspathtree.IndexableLeafTypes and hasattr(item,'__getitem__'):
        return fspathtree(item,root=self.root,abspath=(self.abspath/path).as_posix())
      else:
        return item

    # path is relative
    # first try to get the item from local tree
    # if a PathGoesAboveRoot exception is thrown, then
    # we can check to see if the path refers to an item in the
    # root tree
    try:
      item = fspathtree.getitem(self.tree,path)
    except PathGoesAboveRoot as e:
      if self.abspath == self.PathType("/"):
        raise e

      item = fspathtree.getitem(self.root,(self.abspath/path).relative_to('/'))


    if type(item) not in fspathtree.IndexableLeafTypes and hasattr(item,'__getitem__'):
      return fspathtree(item,root=self.root,abspath=(self.abspath/path).as_posix())
    else:
      return item


  def __setitem__(self,key,value):
    path = self.make_path(key)

    if path.is_absolute():
      fspathtree.setitem(self.root,path.relative_to('/'),value)
      return

    # path is relative
    # first try to set the item from local tree
    # if a PathGoesAboveRoot exception is thrown, then
    # we can check to see if the path refers to an path in the
    # root tree
    try:
      fspathtree.setitem(self.tree,path,value)
    except PathGoesAboveRoot as e:
      if self.abspath == self.PathType("/"):
        raise e
      fspathtree.setitem(self.root,(self.abspath/path).relative_to('/'),value)


  def update(self,*args,**kwargs):
    self.tree.update(*args,**kwargs)

  def path(self):
    return self.normalize_path(self.abspath)

  def get(self,path,default_value):
    '''
    Returns the value of the node references by path, or a default value if the node does not exists.
    '''
    try:
      return self[path]
    except:
      return default_value


  @staticmethod
  def _normalize_path_parts(parts,up="..",current="."):

    if up not in parts and current not in parts:
      return parts

    norm_parts = list()
    for p in parts:
      if p == current:
        continue
      elif p == up:
        if len(norm_parts) < 1:
          return None
        del norm_parts[-1]
      else:
        norm_parts.append(p)

    return norm_parts


  @staticmethod
  def normalize_path(path,up="..",current="."):
    return fspathtree.make_path( fspathtree._normalize_path_parts( path.parts, up, current) )

  @staticmethod
  def getitem(tree,path,normalize_path=True):
    '''
    Given a tree and a path, returns the value of the node pointed to by the path. By default, the path will be normalized first.
    This can be disabled by passing normalize_path=False.
    '''
    if type(path) in (list,tuple):
      parts = path
    else:
      if type(path) is not fspathtree.PathType:
        path = fspathtree.PathType(path)
      parts = path.parts

    if normalize_path:
      parts = fspathtree._normalize_path_parts(parts)

    if parts is None:
      raise PathGoesAboveRoot("fspathtree: Key path contains a parent reference (..) that goes above the root of the tree")

    # TODO: we may need to do some more work here...
    try:
      node = tree[parts[0]]
    except TypeError as e:
      # if getting the node fails,
      # it probably means we have a list
      # and we need to pass it an integer index
      node = tree[int(parts[0])]


    if len(parts) == 1:
      return node
    else:
      return fspathtree.getitem(node,parts[1:])


  @staticmethod
  def setitem(tree,path,value):
    '''
    Given a tree, a path, and a value, sets the value of the node pointed to by the path. If any level of the path does not
    exists, it is created.
    '''
    if type(path) in (list,tuple):
      parts = path
    else:
      if type(path) is not fspathtree.PathType:
        path = fspathtree.PathType(path)
      parts = path.parts

    parts = fspathtree._normalize_path_parts(parts)

    if parts is None:
      raise PathGoesAboveRoot("fspathtree: Key path contains a parent reference (..) that goes above the root of the tree")

    if len(parts) == 1:
      tree[parts[0]] = value
    else:
      # check if item needs to be created
      try:
        x = tree[parts[0]]
      except:
        tree[parts[0]] = fspathtree.DefaultNodeType()

      return fspathtree.setitem(tree[parts[0]],parts[1:],value)

  @staticmethod
  def get_all_leaf_node_paths(node, as_str=False, current_path=PathType("/"), paths=None):
    '''
    Returns a list containing the paths to all leaf nodes in the tree.
    '''
    if paths is None:
      paths = list()
    if type(node) not in fspathtree.IndexableLeafTypes and hasattr(node,'__getitem__'):
      try:
        for i in range(len(node)):
          fspathtree.get_all_leaf_node_paths( node[i], as_str, current_path / str(i), paths )
      except:
        for k in node:
          fspathtree.get_all_leaf_node_paths( node[k], as_str, current_path / k, paths )
    else:
      if as_str:
        paths.append(str(current_path))
      else:
        paths.append(current_path)
  
    return paths

  def _instance_get_all_leaf_node_paths(self, as_str = False, current_path=PathType("/"), paths=None):
    return fspathtree.get_all_leaf_node_paths(self.tree,as_str,current_path,paths)
