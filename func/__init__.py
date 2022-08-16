from . import (
    numbers, 
    strings, 
    date, 
    logic,
)
from .base import Func


_FMODULES = (
    numbers, 
    strings, 
    date, 
    logic,    
)

FUNCTIONS_DICT = {}
for subm in _FMODULES:
    for f in dir(subm):
        p = getattr(subm, f)
        try:
            is_func = issubclass(p, Func)
        except TypeError:
            pass
        else:
            if is_func:
                name = p.__name__.lower()
                FUNCTIONS_DICT[name] = p


