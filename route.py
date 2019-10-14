import functools

from importlib import import_module

from pyws.public import InvalidPath


def route(path):
    def wrapper(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        _wrapper.__route__ = path
        return _wrapper

    return wrapper


class Route:
    routes = {}

    @classmethod
    def add_routes(cls, module_name):
        point = module_name.rfind('.')
        if point == (-1):
            mod = import_module(module_name)
        else:
            mod = getattr(import_module(module_name[:point]), module_name[point + 1:])
        for attr in dir(mod):
            if attr.startswith('_'):
                continue
            func = getattr(mod, attr)
            path = getattr(func, '__route__', None)
            if path and callable(func):
                cls.routes.setdefault(path, func)

    @classmethod
    def get(cls, path):
        func = cls.routes.get(path)
        if not func:
            raise InvalidPath
        return func
