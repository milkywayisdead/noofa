# словарь функций, где ключ - имя функции в нижнем регистре,
# значение - класс функции.
FUNCTIONS_DICT = {}

# аналогичный словарь операторов
OPERATORS_DICT = {}


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
        datastruct,
        typeconv,
    )
    
    fmodules = (
        numbers, 
        strings, 
        date, 
        logic,
        datastruct,
        typeconv,
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


def _collect_operators():
    """
    Сбор операторов в словарь операторов.
    """
    from .base import Func
    from . import operators
    for c in dir(operators):
        p = getattr(operators, c)
        try:
            is_func = issubclass(p, Func)
        except TypeError:
            pass
        else:
            if is_func and hasattr(p, 'sign'):
                OPERATORS_DICT[p.sign] = p


_collect_functions()
_collect_operators()


def collect_description():
    res = {}
    for fname, f in FUNCTIONS_DICT.items():
        fgroup = f.group
        if not fgroup in res:
            res[fgroup] = {}
        desc = f.description
        if desc != '__':
            res[fgroup][fname] = f.description
    return res