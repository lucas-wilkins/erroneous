class Recurse(Exception):
    """ Exception used to convert tail recursion to loop """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


def recurse(*args, **kwargs):
    """ Call this instead of return f(...)"""
    raise Recurse(*args, **kwargs)


def tail_recursive(fun):
    """ Make a tail recursive function"""
    def decorated(*args, **kwargs):
        while True:
            try:
                return fun(*args, **kwargs)
            except Recurse as r:
                args = r.args
                kwargs = r.kwargs
                continue

    return decorated

