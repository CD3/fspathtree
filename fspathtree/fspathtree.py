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

  # Public Instance API

  def __getitem__(self,path):
    path = self._make_path(path)

    if path.is_absolute():
      node = fspathtree.getitem(self.root,path,normalize_path=True)
    else:
      try:
        node = fspathtree.getitem(self.tree,path)
      except PathGoesAboveRoot as e:
        # if the key references a node above th root,
        # try again with the root tree.
        if self.abspath == self.PathType("/"):
          raise e
        node = fspathtree.getitem(self.root,(self.abspath/path))

    # if the item is an indexable node, we want to wrap it in an fspathtree before returning.
    if type(node) not in fspathtree.IndexableLeafTypes and hasattr(node,'__getitem__'):
      return fspathtree(node,root=self.root,abspath=(self.abspath/path).as_posix())
    else:
      return node


  def __setitem__(self,key,value):
    path = self._make_path(key)

    if path.is_absolute():
      fspathtree.setitem(self.root,path,value)
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
      fspathtree.setitem(self.root,(self.abspath/path),value)


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




  # Public Static API



  @staticmethod
  def normalize_path(path,up="..",current="."):
    parts = fspathtree._normalize_path_parts( path.parts, up, current)
    if parts is None:
      return None
    return fspathtree.PathType(*parts)

  @staticmethod
  def getitem(tree,path,normalize_path=True):
    '''
    Given a tree and a path, returns the value of the node pointed to by the path. By default, the path will be normalized first.
    This can be disabled by passing normalize_path=False.

    path may be specified as a string, Path-like object, or list of path elements.
    '''
    path = fspathtree._make_path(path,normalize_path=False)
    # remove the '/' from the beginning of the path if it exists.
    if path.is_absolute():
      path = path.relative_to('/')

    return fspathtree._getitem_from_path_parts(tree,path.parts,normalize_path)


  @staticmethod
  def setitem(tree,path,value,normalize_path=True):
    '''
    Given a tree, a path, and a value, sets the value of the node pointed to by the path. If any level of the path does not
    exists, it is created.
    '''
    path = fspathtree._make_path(path,normalize_path=False)
    # remove the '/' from the beginning of the path if it exists.
    if path.is_absolute():
      path = path.relative_to('/')

    fspathtree._setitem_from_path_parts(tree,path.parts,value,normalize_path)

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

  # this is used to allow the same name for instance and static methods
  def _instance_get_all_leaf_node_paths(self, as_str = False, current_path=PathType("/"), paths=None):
    return fspathtree.get_all_leaf_node_paths(self.tree,as_str,current_path,paths)




  # Private Methods

  @staticmethod
  def _make_path(key,normalize_path=False):
    '''
    Given a string, bytes array, integer, or list of path elements;  return a PathType object representing the path.
    '''
    if type(key) in (list,tuple):
      path = fspathtree.PathType(*key)
    else:
      if type(key) in (str,bytes):
        key = re.sub(r'^\/+','/',key) # replace multiple '/' at front with a single '/'. i.e. // -> /

      if type(key) in (int,):
        key = str(key)
      path = fspathtree.PathType(key)

    if normalize_path:
      path = fspathtree.normalize_path(path)
      if path is None:
        raise PathGoesAboveRoot("fspathtree: Key path contains a parent reference (..) that goes above the root of the tree")

    return path

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
  def _getitem_from_path_parts(tree,parts,normalize_path=True):

    if normalize_path:
      parts = fspathtree._normalize_path_parts(parts)

    if parts is None:
      raise PathGoesAboveRoot("fspathtree: Key path contains a parent reference (..) that goes above the root of the tree")

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
      return fspathtree._getitem_from_path_parts(node,parts[1:],False)

  @staticmethod
  def _setitem_from_path_parts(tree,parts,value,normalize_path=True):

    if normalize_path:
      parts = fspathtree._normalize_path_parts(parts)

    if parts is None:
      raise PathGoesAboveRoot("fspathtree: Key path contains a parent reference (..) that goes above the root of the tree")

    if len(parts) == 1:
      try:
        tree[parts[0]] = value
      except TypeError as e:
        # if getting the node fails,
        # it probably (hopefully) means we have a list
        # and we need to pass it an integer index
        tree[int(parts[0])] = value
    else:
      # check if item needs to be created
      try:
        x = tree[parts[0]]
      except:
        tree[parts[0]] = fspathtree.DefaultNodeType()

      fspathtree._setitem_from_path_parts(tree[parts[0]],parts[1:],value,False)


