"""
Функции подключения к источникам.
"""

from webbrowser import get
from ..sources.conn import get_source_class
from .base import ConnectionFunc, MandatoryArg


class NewConnection(ConnectionFunc):
    """
    Функция создания подключения к источнику.
    """
    description = 'Функция создания подключения к источнику'
    args_description = [
        MandatoryArg('Тип источника', 0),
        MandatoryArg('Строка подключения', 1),
    ]

    @classmethod
    def get_name(cls):
        return 'new_connection'

    def _operation(self, *args):
        conn = get_source_class(args[0])
        conn = conn(conn_str=args[1])
        return conn