"""
Для профилей отчётов.
"""
from .core import Panda, _SOURCES_DICT


class ReportSchema:
    def __init__(self, **kwargs):
        _sources = kwargs.get('sources', {})
        _dataframes = kwargs.get('dataframes', {})
        _queries = kwargs.get('queries', {})

        self._sources = SourcesSet()
        self._dataframes = DataframesSet()
        for k, source_params in _sources.items():
            self.add_source(Source(**source_params))
        for k, df_params in _dataframes.items():
            self.add_dataframe(Dataframe(**df_params))

    def add_source(self, source):
        self._sources.add(source)

    def add_dataframe(self, df):
        self._dataframes.add(df)

    @property
    def sources(self):
        return self._sources

    @property
    def dataframes(self):
        return self._dataframes


class SourcesSet:
    def __init__(self, **kwargs):
        self._sources = kwargs.get('sources', {})
        self._tables = kwargs.get('tables', [])

    def add(self, source):
        self._sources[source.name] = source

    def __getitem__(self, value):
        return self._sources[value]


class DataframesSet:
    def __init__(self, **kwargs):
        self._dataframes = kwargs.get('dataframes', {})

    def add(self, df):
        self._dataframes[df.name] = df

    def __getitem__(self, value):
        return self._dataframes[value]


class Source:
    """
    Источник в профиле отчёта.
    """
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self._connection = None  # соединение (экз. класса *Source из sources.conn)
        self._tables = kwargs.get('tables', {})  #  таблицы
        self._queries = {}  # запросы
        type_ = kwargs.pop('type')
        kwargs.pop('name')
        source_cls = _SOURCES_DICT[type_]
        self._connection = source = source_cls(**kwargs)

    def open(self):
        if self._connection.connection is None:
            self._connection.open()

    def close(self):
        self._connection.close()


class Query:
    """
    Запрос в профиле отчёта.
    """
    def __init__(self, **kwargs):
        self.name = kwargs['name']  # название/идентиф. запроса
        self._source = kwargs['source']  # источник
        self._query = kwargs['query']  # объект запроса (из sources.query)

    def execute(self):
        """
        Выполнение запроса.
        """
        data = self._source.get_data(query=self._query)
        return data


class Dataframe:
    """
    Датафрейм в профиле отчёта.
    """
    def __init__(self, **kwargs):
        self.name = kwargs['name']  # название датафрейма
        self._query = kwargs.get('from', None) #  из результатов какого запроса строить датафрейм
        self._columns = kwargs.get('columns', [])  # список полей, которые нужно оставить
        self._aliases = kwargs.get('aliases', {})  # поля, которые нужно переименовать
        self._df = Panda(kwargs.get('data'), {})  # датафрейм

    @property
    def from_query(self):
        return self._query


test_conf = {
    'sources': {
        'test': {
            'name': 'test',
            'type': 'postgres',
            'host': 'localhost',
            'port': 5432,
            'dbname': 'reports',
            'user': 'max',
            'password': '12345',
        },
        'mysql': {
            'type': 'mysql',
            'name': 'mysql',
            'host': 'localhost',
            'port': 3306,
            'dbname': 'test',
            'user': 'max',
            'password': '12345',
        }
    },
}

"""
Конфигурация профиля

{
    # словарь с источниками
    sources: {
        name1: {
            name: название,
            type: тип,
            host: хост,
            port: порт,
            dbname: имя базы,
            user: имя пользователя,
            password: пароль,
        }
    },

    # словарь с запросами
    queries: {
        source: название источника,
        ... тело запроса,
    },

    # словарь с датафреймами
    {

    }
}
"""