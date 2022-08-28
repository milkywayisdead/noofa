"""
Для профилей отчётов.
"""
from .core import Panda, _SOURCES_DICT


class ReportSchema:
    def __init__(self, **kwargs):
        _sources = kwargs.get('sources', SourcesSet())
        _dataframes = kwargs.get('dataframes', DataframesSet())

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

    @staticmethod
    def from_json(json_schema={}):
        schema = ReportSchema()
        sources = json_schema.get('sources', {})
        dataframes = json_schema.get('dataframes', {})
        sources_set = SourcesSet()
        dataframes_set = DataframesSet()

        for n, s in sources.items():
            source = Source(s)
            sources_set.add(source)

        schema.sources = sources_set
        schema.dataframes = dataframes_set

        return schema


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
        if self._connection.connection is not None:
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