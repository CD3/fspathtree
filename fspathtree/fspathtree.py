from pathlib import PurePosixPath
import re

class PathGoesAboveRoot(Exception):
  pass

class fspathtree:
  """A small class that wraps a tree data struction and allow accessing the nested elements using filesystem-style paths."""
  DefaultNodeType = dict
  PathType = PurePosixPath
  IndexableLeafType = (str,bytes)

  def __init__(self,tree=DefaultNodeType(),root=None,abspath='/'):
    self.tree = tree
    self.root = root if root is not None else tree

    self.abspath = self.PathType(abspath)
    
    if self.tree == self.root and abspath != '/':
      raise RuntimeError("fspathtree: tree initialized with a root, but abspath is not '/'.")

    if self.tree != self.root and abspath == '/':
      raise RuntimeError("fspathtree: tree initialized with an abspath '/', but the tree and root are not the same.")

  def make_path(self,key):
    if type(key) in (str,bytes):
      key = re.sub(r'^\/+','/',key) # replace multiple '/' at front with a single '/'. i.e. // -> /
    if type(key) in (int,):
      key = str(key)

    return self.PathType(key)


  def __getitem__(self,key):
    path = self.make_path(key)

    if path.is_absolute():
      item = fspathtree.getitem(self.root,path.relative_to('/').parts)
      if type(item) not in fspathtree.IndexableLeafType and hasattr(item,'__getitem__'):
        return fspathtree(item,root=self.root,abspath=(self.abspath/path).as_posix())
      else:
        return item

    # path is relative
    # first try to get the item from local tree
    # if a PathGoesAboveRoot exception is thrown, then
    # we can check to see if the path refers to an item in the
    # root tree
    try:
      item = fspathtree.getitem(self.tree,path.parts)
    except PathGoesAboveRoot as e:
      if self.abspath == self.PathType("/"):
        raise e

      item = fspathtree.getitem(self.root,(self.abspath/path).relative_to('/').parts)


    if type(item) not in fspathtree.IndexableLeafType and hasattr(item,'__getitem__'):
      return fspathtree(item,root=self.root,abspath=(self.abspath/path).as_posix())
    else:
      return item


  def __setitem__(self,key,value):
    path = self.make_path(key)

    if path.is_absolute():
      fspathtree.setitem(self.root,path.relative_to('/').parts,value)
      return

    # path is relative
    # first try to set the item from local tree
    # if a PathGoesAboveRoot exception is thrown, then
    # we can check to see if the path refers to an path in the
    # root tree
    try:
      fspathtree.setitem(self.tree,path.parts,value)
    except PathGoesAboveRoot as e:
      if self.abspath == self.PathType("/"):
        raise e
      fspathtree.setitem(self.root,(self.abspath/path).relative_to('/').parts,value)


  def update(self,*args,**kwargs):
    self.tree.update(*args,**kwargs)

  def path(self):
    return self.make_path('/'.join(self.normalize_path_parts(self.abspath.parts)))

  def get(self,key,default_value):
    try:
      return self[key]
    except:
      return default_value



  @staticmethod
  def normalize_path_parts(parts,up="..",current="."):
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
  def getitem(tree,parts,normalize_path=True):
    if normalize_path:
      parts = fspathtree.normalize_path_parts(parts)

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
      return fspathtree.getitem(node,parts[1:],normalize_path = False)


  @staticmethod
  def setitem(tree,parts,value):
    parts = fspathtree.normalize_path_parts(parts)
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

