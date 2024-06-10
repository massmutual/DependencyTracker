from collections import OrderedDict

class CachedAttr(object):
    '''Computes attribute value and caches it in instance.

    Example:
        class MyClass(object):
            def myMethod(self):
                # ...
            myMethod = Cached(myMethod)
    Use "del inst.myMethod" to clear cache.
    http://code.activestate.com/recipes/276643/
    '''
    def __init__(self, method, name=None):
        self.method = method
        self.name = name or method.__name__

    def __get__(self, inst, cls):
        if inst is None:
            return self
        result = self.method(inst)
        setattr(inst, self.name, result)
        return result


def resolve_name(name, module_name=None, raise_exc=False):
    '''Given a name string and module prefix, try to import the name.
    '''
    if not isinstance(name, str):
        raise TypeError('Need a stringy name to import.')
    if module_name is None:
        module_name, _, name = name.rpartition('.')
    try:
        module = __import__(module_name, globals(), locals(), [name], 0)
    except ImportError as exc:
        if raise_exc:
            raise exc
    else:
        return getattr(module, name)


class ShellPath(object):

    def __init__(self, path_str, delimiter=':'):
        self.paths = OrderedDict()
        if path_str:
            self.paths = self.decompose(path_str, delimiter)
        self.delimiter = delimiter

    def __str__(self):
        return self.compose(self.paths, self.delimiter)

    def __len__(self):
        return len(self.paths)

    def __contains__(self, path):
        return path in self.paths

    def __iter__(self):
        return iter(self.paths.keys())

    def __getstate__(self):
        return {'path_str': str(self),
                'delimiter': self.delimiter}

    def __setstate__(self, state):
        self.__dict__['delimiter'] = state['delimiter']
        self.__dict__['paths'] = self.decompose(state['path_str'],
                                                state['delimiter'])
    
    @staticmethod
    def decompose(path_str, delimiter):
        return OrderedDict([(k, True) for k in
                            path_str.split(delimiter)])

    @staticmethod
    def compose(paths, delimiter):
        return delimiter.join(paths.keys())

    def append(self, path):
        """stick a path into paths at the end (the last place the shell will
        look).

        """
        self.paths[path] = True
        self.paths.move_to_end(path)

    def prepend(self, path):
        """stick a path into paths at the beginning (the first place the shell
        will look).

        """
        self.paths[path] = True
        self.paths.move_to_end(path, last=False)

    def remove(self, path):
        del self.paths[path]
