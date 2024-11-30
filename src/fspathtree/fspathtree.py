import collections
import copy
import re
from inspect import signature
from pathlib import PurePosixPath


class PathGoesAboveRoot(Exception):
    pass


class CannotCreateParentNode(Exception):
    pass


class InvalidIndexError(IndexError):
    pass


class UnrecognizedParentNodeType(Exception):
    def __init__(self, node_type, remaining_parts):
        self.node_type = node_type
        self.remaining_parts = remaining_parts


class NodeError(Exception):
    pass


class fspathtree:
    """A small class that wraps a tree data struction and allow accessing the nested elements using filesystem-style paths."""

    MappingNodeType = dict
    SequenceNodeType = list
    DefaultNodeType = MappingNodeType
    PathType = PurePosixPath

    def __init__(self, tree=None, root=None, abspath="/"):
        # we don't want to created "nested" fspathtree objects
        # beccause we want them to be light wrappers around regular
        # types. so, if tree is an fspathtree instance, we want to
        # wrap its tree instead
        if isinstance(tree, fspathtree):
            tree = tree.tree
        self.tree = tree if tree is not None else self.DefaultNodeType()
        self.root = root if root is not None else self.tree

        self.abspath = self.PathType(abspath)

        if self.tree == self.root and abspath != "/":
            raise RuntimeError(
                "fspathtree: tree initialized with a root, but abspath is not '/'."
            )

        if self.tree != self.root and abspath == "/":
            raise RuntimeError(
                "fspathtree: tree initialized with an abspath '/', but the tree and root are not the same."
            )

        self.get_all_paths = self._instance_get_all_paths
        self.get_all_leaf_node_paths = self._instance_get_all_leaf_node_paths
        self.find = self._instance_find

    @staticmethod
    def _make_node_type_for_key(key):
        if key.isnumeric():
            return fspathtree.SequenceNodeType()
        return fspathtree.MappingNodeType()

    @staticmethod
    def is_leaf(node):
        """Return true if node is a leaf. i.e. not a mapping or list."""
        if type(node) in [str, bytes]:
            return True

        if isinstance(node, collections.abc.Mapping) or isinstance(
            node, collections.abc.Sequence
        ):
            return False

        return True

    # Public Instance API

    def __getitem__(self, path, wrap_branch_nodes=True):
        """
        Return node located at `path`.

        `path` is a '/' separated list of keys/indices to the node.
        """
        path = self._make_path(path)

        if path.is_absolute():
            node = fspathtree.getitem(self.root, path)
        else:
            try:
                node = fspathtree.getitem(self.tree, path)
            except PathGoesAboveRoot as e:
                # if the key references a node above th root,
                # try again with the root tree.
                if self.abspath == self.PathType("/"):
                    raise e
                node = fspathtree.getitem(self.root, (self.abspath / path))

        # if the item is an indexable node, we want to wrap it in an fspathtree before returning.
        if fspathtree.is_leaf(node) or wrap_branch_nodes is False:
            return node
        else:
            return fspathtree(
                node, root=self.root, abspath=(self.abspath / path).as_posix()
            )

    def __setitem__(self, path, value):
        """
        Set the element located at `path` to `value`.

        The `path` is treated as a filesystem-like path, with parts separated by '/' characters.
        If the path represented by `path` includes "parents" that do not exists, they will be created.
        """
        path = self._make_path(path)

        if path.is_absolute():
            fspathtree.setitem(self.root, path, value)
            return

        # path is relative
        # first try to set the item from local tree
        # if a PathGoesAboveRoot exception is thrown, then
        # we can check to see if the path refers to an path in the
        # root tree
        try:
            fspathtree.setitem(self.tree, path, value)
        except PathGoesAboveRoot as e:
            if self.abspath == self.PathType("/"):
                raise e
            fspathtree.setitem(self.root, (self.abspath / path), value)

    def __contains__(self, path):
        try:
            self[path]
            return True
        except:
            return False

    def __len__(self):
        return len(self.tree)

    def update(self, *args, **kwargs):
        """
        Update tree with entries from another fspathtree and/or dict/list.

        Note: if an fspathtree is passed as an argument, then the tree is updated recursively. If a dict is passed,
        then the standard dict.update(...) method is used. This means that tree branches will be overwritten if
        passing a plain dict.
        """
        # if _any_ of the arguments are an fspathtree, then
        # we want to implemented a nested update.
        if any([isinstance(a, fspathtree) for a in args]):
            for a in args:
                if type(a) is dict:
                    a = fspathtree(
                        a
                    )  # convert all non-trees to trees, so we can subscript them with path keys

                for key in a.get_all_leaf_node_paths():
                    self[key] = a[key]

            for key in kwargs:
                self[key] = kwargs[key]

        else:
            # otherwise, we just use the
            self.tree.update(*args, **kwargs)

    def path(self):
        """
        Return absolute path to the current node.

        Note that leaf notes are returned as thier value and lose knowlege of being part
        of a "tree". For example, this does not work

            tree['/one/two/three'] = 3
            assert tree['/one/two/three'].path() == '/one/two/three'

        because the call to tree['/one/two/three'] returns the integer 3.
        i.e. it does not return a proxy type that keeps track of the tree.

        If you want tree values that 'know' about their location in the
        tree, use a special key name for values

            tree['/one/two/three/@value'] = 3
            assert tree['/one/two/three'].path() == '/one/two/three'
            assert tree['/one/two/three'][@value] == 3
        """
        return self.normalize_path(self.abspath)

    def get(self, path, default_value):
        """
        Returns the value of the node references by path, or a default value if the node does not exist.
        """
        try:
            return self[path]
        except KeyError:
            return default_value

    # this is used to allow the same name for instance and static methods
    def _instance_get_all_paths(self, transform=None, predicate=None):
        root_path = fspathtree.PathType("")
        if self.tree == self.root:
            root_path = fspathtree.PathType("/")

        return fspathtree.get_all_paths(
            self.tree, transform, predicate, root_path=root_path
        )

    def _instance_get_all_leaf_node_paths(self, transform=None, predicate=None):
        root_path = fspathtree.PathType("")
        if self.tree == self.root:
            root_path = fspathtree.PathType("/")

        return fspathtree.get_all_leaf_node_paths(
            self.tree, transform, predicate, root_path=root_path
        )

    def _instance_find(self, pattern):
        root_path = fspathtree.PathType("")
        if self.tree == self.root:
            root_path = fspathtree.PathType("/")

        return fspathtree.find(self.tree, pattern, root_path=root_path)

    # Public Static API

    @staticmethod
    def normalize_path(path, up="..", current="."):
        """
        Return a normalized version of given path.
        Normalization removes all '..' and '.' elements.

        /one/two/three/../../four  -> /one/four
        """
        path = fspathtree._make_path(path)
        parts = fspathtree._normalize_path_parts(path.parts, up, current)
        if parts is None:
            return None
        return fspathtree.PathType(*parts)

    @staticmethod
    def getitem(tree, path):
        """
        Given a tree and a path, returns the value of the node pointed to by the path. The path will be normalized first.

        path may be specified as a string, Path-like object, or list of path elements.
        """
        original_path = copy.copy(path)
        path = fspathtree._make_path(path)
        # remove the '/' from the beginning of the path if it exists.
        if path.is_absolute():
            path = path.relative_to("/")
        if str(path) == "" or str(path) == ".":
            return tree

        try:
            return fspathtree._getitem_from_path_parts(tree, path.parts)
        # catch exeptions, add some context, and rethrow
        except KeyError as e:
            msg = f"Error while parsing path '{original_path}'. Could not find path element '{e.args[0]}'."
            raise KeyError(msg)
        except (
            InvalidIndexError
        ) as e:  # need to check this one first since it is a sub-class of IndexError
            msg = f"Error while parsing path '{original_path}'. '{e.args[0]}' out of range for Sequence node index."
            raise InvalidIndexError(msg)
        except IndexError as e:
            msg = f"Error while parsing path '{original_path}'. Could not find path element '{e.args[0]}'."
            raise IndexError(msg)
        except ValueError as e:
            msg = f"Error while parsing path '{original_path}'. Could not convert '{e.args[0]}' to an integer for indexing Sequence node."
            raise ValueError(msg)
        except Exception as e:
            raise e

    @staticmethod
    def setitem(tree, path, value):
        """
        Given a tree, a path, and a value, sets the value of the node pointed to by the path. If any level of the path does not
        exist, it is created. If the _root_ node type needs to be changed to set the value, then a new tree with the value set
        is returned.
        """
        original_path = copy.copy(path)
        path = fspathtree._make_path(path)
        # remove the '/' from the beginning of the path if it exists.
        if path.is_absolute():
            path = path.relative_to("/")

        try:
            return fspathtree._setitem_from_path_parts(tree, path.parts, value)
        except KeyError as e:
            msg = f"Error while parsing path '{original_path}'. Could not find path element '{e.args[0]}'."
            raise KeyError(msg)
        except (
            InvalidIndexError
        ) as e:  # need to check this one first since it is a sub-class of IndexError
            msg = f"Error while parsing path '{original_path}'. '{e.args[0]}' out of range for Sequence node index."
            raise InvalidIndexError(msg)
        except IndexError as e:
            msg = f"Error while parsing path '{original_path}'. Could not find path element '{e.args[0]}'."
            raise IndexError(msg)
        except ValueError as e:
            msg = f"Error while parsing path '{original_path}'. Could not convert '{e.args[0]}' to an integer for indexing Sequence node."
            raise ValueError(msg)
        except Exception as e:
            raise e

    @staticmethod
    def get_all_paths(node, transform=None, predicate=None, root_path=PathType()):
        if transform is False:
            transform = None
        return fspathtree._get_all_paths(node, transform, predicate, root_path)

    @staticmethod
    def get_all_leaf_node_paths(
        node, transform=None, predicate=None, root_path=PathType()
    ):
        """
        Return a list of all paths that point leaf notes (i.e. point to values)

        `transform` is an optional callable that can be used to transform the paths
        before returning. This can be used to remove leading '/' for example.
        Each leaf node path will be passed to `transform(path)` and the return value
        will be returned.

        `predicate` is an optional callable that can be used to determine if the path
        should be returned. This is useful for filting leaf node paths.
        """
        if transform is False:
            transform = None
        return fspathtree._get_all_leaf_node_paths(
            node, transform, predicate, root_path
        )

    @staticmethod
    def find(tree, pattern, as_string=False, root_path=PathType()):
        """
        Return all leaf node paths matching `pattern`.
        """
        return fspathtree.get_all_leaf_node_paths(
            tree,
            str if as_string else None,
            lambda p: p.match(pattern),
            root_path=root_path,
        )

    # Private Methods

    @staticmethod
    def _make_path(key):
        """
        Given a string, bytes array, integer, or list of path elements;  return a PathType object representing the path.
        """
        if type(key) == fspathtree.PathType:
            return key

        if type(key) in (list, tuple):
            path = fspathtree.PathType(*key)
        else:
            if type(key) in (str, bytes):
                key = re.sub(
                    r"^\/+", "/", key
                )  # replace multiple '/' at front with a single '/'. i.e. // -> /

            if type(key) in (int,):
                key = str(key)
            path = fspathtree.PathType(key)

        return path

    @staticmethod
    def _normalize_path_parts(parts, up="..", current="."):
        """
        Normalize a list of path parts. i.e. remove ".." and "." elements
        while maintaining the same path.
        """

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
    def _getitem_from_path_parts(tree, path_parts):
        """
        @param tree           A nested Mapping/Sequence (i.e. dict/list) object that is being accessed.
        @param path_parts     A list of path elements identifying the location of the element being accessed.
        """
        # normalize the path before traversing
        path_parts = fspathtree._normalize_path_parts(path_parts)

        if path_parts is None:
            raise PathGoesAboveRoot(
                "fspathtree: Key path contains a parent reference (..) that goes above the root of the tree"
            )

        try:
            return fspathtree._getitem_from_path_parts_imp(tree, path_parts)
        except UnrecognizedParentNodeType as e:
            # If at any point during the traversal we run into a node that we cannot figure out
            # how to subscript, we will throw an UnrecognizedParentNodeType esception. However,
            # we don't want to throw that to the caller, becasue it will not have any information
            # about where in the path the error occured. So, we will catch this exception,
            # figure out where it happened, and throw a nicer error.
            error_node_path_parts = [
                p for p in path_parts if p not in e.remaining_parts
            ]
            raise NodeError(
                f"Unknown parent node type ({e.node_type}) found at '{'/'.join(error_node_path_parts)}' while traversing path '{'/'.join(path_parts)}'. This likely means you are trying to access an element beyond a current leaf node."
            )

    def _getitem_from_path_parts_imp(tree, path_parts):
        if isinstance(tree, collections.abc.Mapping):
            # node is a mapping (i.e. is indexed by a string like a dict)
            # check if node contains the current path_part as a key
            if path_parts[0] in tree:
                node = tree[path_parts[0]]
            else:
                raise KeyError(path_parts[0])
        elif isinstance(tree, collections.abc.Sequence):
            # node is a sequence (i.e. is indexed by a string like a list)
            # check that the path_part is actually an integer
            if path_parts[0].isnumeric():
                idx = int(path_parts[0])
            else:
                raise ValueError(path_parts[0])

            # check if node contains the current path_part as an index
            if len(tree) > idx:
                node = tree[idx]
            else:
                raise InvalidIndexError(idx)
        else:
            # if it isn't a mapping or sequence, we don't know how to
            # index it.
            raise UnrecognizedParentNodeType(type(tree), path_parts)

        # the element (appears) to exists.
        # check to see if it is a leaf node or if we need to keep walking the path.
        if len(path_parts) == 1:
            return node
        else:
            return fspathtree._getitem_from_path_parts_imp(node, path_parts[1:])

    @staticmethod
    def _setitem_from_path_parts(tree, path_parts, value):
        """
        Set the value of a tree branch located at the path given by `path_parts` to the given value.
        Any missing "parents" of the path are created.

        @param tree           A nested Mapping/Sequenhe (i.e. dict/list) object that is being accessed.
        @param path_parts     A list of path elements identifying the location of the element being accessed.
        @param value          Value to set node at path to.
        """

        path_parts = fspathtree._normalize_path_parts(path_parts)

        if path_parts is None:
            raise PathGoesAboveRoot(
                "fspathtree: Key path contains a parent reference (..) that goes above the root of the tree"
            )

        fspathtree._setitem_from_path_parts_imp(tree, path_parts, value)

    @staticmethod
    def _setitem_from_path_parts_imp(tree, path_parts, value):
        key = path_parts[0]
        # if the tree is a dict, then add the path as a key
        if isinstance(tree, collections.abc.Mapping):
            if len(path_parts) == 1:
                tree[key] = value
            else:
                if key not in tree:
                    tree[key] = fspathtree._make_node_type_for_key(path_parts[1])
                result = fspathtree._setitem_from_path_parts_imp(
                    tree[key], path_parts[1:], value
                )
                if result is not None:
                    tree[key] = result
                    fspathtree._setitem_from_path_parts_imp(
                        tree[key], path_parts[1:], value
                    )

        # if the tree is a list, then add the path as an elment of the list with given index
        elif isinstance(tree, collections.abc.Sequence):
            # check that the path element is an integer.
            # if it is not, then we want to convert the list to a dict
            # and tell the caller to try again...
            if not key.isnumeric():
                raise ValueError(key)

            key = int(key)

            # if the list does not have enough elements
            # append None until it does
            while len(tree) <= key:
                tree.append(None)
            if len(path_parts) == 1:
                tree[key] = value
            else:
                if tree[key] is None:
                    tree[key] = fspathtree._make_node_type_for_key(path_parts[1])
                result = fspathtree._setitem_from_path_parts_imp(
                    tree[key], path_parts[1:], value
                )
                if result is not None:
                    tree[key] = result
                    fspathtree._setitem_from_path_parts_imp(
                        tree[key], path_parts[1:], value
                    )
        else:
            # if we are here, then it means this node has _previously_ been set to a scalar.
            # i.e.
            # t['/level1/level2'] = 1
            # t['/level1/level2/level3'] = 1 # level2 is not a dict or list!
            # we want to support this, so we need to convert the node. if the path
            # element is an int (or convertable to an int), then we want to replace
            # the node with a list, otherwise, we will replace it with a dict.
            # we will return an empty version of the new node type so that the caller (above)
            # can replace the node and try again.
            if path_parts[0].isnumeric():
                return fspathtree.SequenceNodeType()
            return fspathtree.MappingNodeType()
            raise CannotCreateParentNode(
                f"fspathree: unrecognized node type '{type(tree)}' is not Mapping or Sequence. Do not know how to set item."
            )

    @staticmethod
    def _get_all_paths(node, transform=None, predicate=None, root_path=PathType()):
        """
        Return a list of all paths in the tree.
        """
        return_path = True
        if predicate is not None:
            num_args = len(signature(predicate).parameters)
            if num_args == 1:
                return_path = predicate(root_path)
            elif num_args == 2:
                return_path = predicate(root_path, node)
            else:
                raise RuntimeError(
                    f"fspathtree: Predicate function not supported. Predicates may take 1 or 2 arguments. Provided function takes {num_args}."
                )

        if return_path:
            if transform is None:
                yield root_path
            elif type(transform) == type:
                yield transform(root_path)
            else:
                num_args = len(signature(transform).parameters)
                if num_args == 1:
                    yield transform(root_path)
                elif num_args == 2:
                    yield transform(root_path, node)
                else:
                    raise RuntimeError(
                        f"fspathtree: Transform function not supported. Transforms may take 1 or 2 arguments. Provided function takes {num_args}."
                    )

        if not fspathtree.is_leaf(node):
            try:
                for i in range(len(node)):
                    yield from fspathtree._get_all_paths(
                        node[i], transform, predicate, root_path / str(i)
                    )
            except:
                for k in node:
                    yield from fspathtree._get_all_paths(
                        node[k], transform, predicate, root_path / k
                    )

    @staticmethod
    def _get_all_leaf_node_paths(
        node, transform=None, predicate=None, root_path=PathType()
    ):
        """
        Returns a list containing the paths to all leaf nodes in the tree.
        """
        # we can use the _get_all_paths(...) function if just add is_leaf to the predicate.
        new_predicate = lambda p, n: fspathtree.is_leaf(n)
        if predicate is not None:
            num_args = len(signature(predicate).parameters)
            if num_args == 1:
                new_predicate = lambda p, n: fspathtree.is_leaf(n) and predicate(p)
            elif num_args == 2:
                new_predicate = lambda p, n: fspathtree.is_leaf(n) and predicate(p, n)
            else:
                raise RuntimeError(
                    f"fspathtree: Predicate function not supported. Predicates may take 1 or 2 arguments. Provided function takes {num_args}."
                )

        for path in fspathtree._get_all_paths(
            node, transform, new_predicate, root_path
        ):
            yield path
