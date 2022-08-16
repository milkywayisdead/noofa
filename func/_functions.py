# словарь функций, где ключ - имя функции в нижнем регистре,
# значение - класс функции.
FUNCTIONS_DICT = {}


def _collect_functions():
    """
    Сбор функций из подмодулей в словарь функций.
    """
    from .base import Func
    from . import (
        numbers, 
        strings, 
        date, 
        logic,
    )
    
    fmodules = (
        numbers, 
        strings, 
        date, 
        logic,    
    )
    for fmod in fmodules:
        for f in dir(fmod):
            p = getattr(fmod, f)
            try:
                is_func = issubclass(p, Func)
            except TypeError:
                pass
            else:
                if is_func:
                    name = p.__name__.lower()
                    FUNCTIONS_DICT[name] = p


_collect_functions()