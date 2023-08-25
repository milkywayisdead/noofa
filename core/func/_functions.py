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
        df,
        statistics,
        sql,
        conn,
    )

    fmodules = (
        numbers,
        strings,
        date,
        logic,
        datastruct,
        typeconv,
        df,
        statistics,
        sql,
        conn,
    )
    for fmod in fmodules:
        for f in dir(fmod):
            p = getattr(fmod, f)
            try:
                is_func = issubclass(p, Func)
            except TypeError:
                pass
            else:
                if is_func and p.get_description() != '__':
                    name = p.get_name()
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


def collect_func_info():
    """
    Сбор информации по функциям.
    """
    res = {}
    for fname, f in FUNCTIONS_DICT.items():
        fgroup = f.get_group()
        if not fgroup in res:
            res[fgroup] = {}
        #res[fgroup][fname] = f.get_description()
        res[fgroup][fname] = f.get_func_info()
    return res


_collect_functions()
_collect_operators()
