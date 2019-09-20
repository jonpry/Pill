"""Symbolic global constants, like 'None', 'NOT_FOUND', etc."""

__all__ = [
    'Symbol','NOT_GIVEN','NOT_FOUND'
]


class Symbol(object):

    """Symbolic global constant"""

    __slots__ = ['_name', '_module']
    __name__   = property(lambda s: s._name)
    __module__ = property(lambda s: s._module)

    def __init__(self, symbol, moduleName):
        self.__class__._name.__set__(self,symbol)
        self.__class__._module.__set__(self,moduleName)

    def __reduce__(self):
        return self._name

    def __setattr__(self,attr,val):
        raise TypeError("Symbols are immutable")

    def __repr__(self):
        return self.__name__

    __str__ = __repr__


NOT_GIVEN   = Symbol("NOT_GIVEN", __name__)
NOT_FOUND   = Symbol("NOT_FOUND", __name__)

