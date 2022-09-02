"""
Для профилей отчётов.
"""
from pandas import DataFrame

from .utils import get_source_class, collect_tables, Qbuilder


class DataSchema:
    """
    Схема получения данных профиля.
    """
    def __init__(self, **kwargs):
        self._sources = kwargs.get('sources', {})
        self._queries = kwargs.get('queries', {})
        self._dataframes = kwargs.get('dataframes', {})

    def add_source(self, **options):
        name = options.pop('name')
        type_ = options.pop('type')
        source_cls = get_source_class(type_)
        conn = source_cls(**options)
        self._sources[name] = SchemaSource(name, connection=conn)
        return self

    def add_query(self, **options):
        name = options['name']
        source_name = options['source']
        source = self._sources[source_name]
        query_as_json = options['query']
        self._queries[name] = SchemaQuery(name, query_as_json, source)
        return self

    def add_dataframe(self, **options):
        name = options['name']
        source = self._sources[options['source']]
        if not source.is_sql:
            query = None
        else:
            query = self._queries[options['query']]
        self._dataframes[name] = SchemaDataframe(name, source, query)
        return self     

    def from_json(self, json_schema):
        sources_schema = json_schema.get('sources', {})
        queries = json_schema.get('queries', {})
        dataframes = json_schema.get('dataframes', {})
        for options in sources_schema.values():
            self.add_source(**options)
        for options in queries.values():
            self.add_query(**options)
        for options in dataframes.values():
            self.add_dataframe(**options)
        return self


class SchemaSource:
    """
    Источник в схеме профиля.
    """
    def __init__(self, name, **kwargs):
        self.name = name
        self.connection = kwargs.get('connection', None)

    @property
    def is_opened(self):
        return self.connection.connection is not None

    def open(self):
        if not self.is_opened:
            self.connection.open()

    def close(self):
        self.connection.close()

    def get_table(self, table_name):
        return self.connection.get_table(table_name)

    @property
    def is_sql(self):
        return self.connection.is_sql

    def get_data(self, **kwargs):
        source = self.connection
        query = kwargs.get('query', None)
        if query is not None:
            return source.get_data(query=query)
        return source.get_data()


class SchemaQuery:
    """
    Запрос в схеме профиля.
    """
    def __init__(self, name, query_as_json, source=None):
        self.name = name
        self._query_as_json = query_as_json
        self._source = source

    def compile(self):
        """
        Создание объекта запроса (SelectQuery из noofa.core.conn.query).
        """
        query = self._query_as_json
        tables_list = collect_tables(query)
        if not self._source.is_opened:
            self._source.open()
        tables = {t: self._source.get_table(t) for t in tables_list}
        qbuilder = Qbuilder(tables, query)
        return qbuilder.parse_query()


class SchemaDataframe:
    """
    Датафрейм в схеме профиля.
    """
    def __init__(self, name, source, query=None):
        self.name = name
        self._source = source
        self._query = query
        
    def compile(self):
        if self._source.is_sql:
            query = self._query.compile()
            data = self._source.get_data(query=query)
        else:
            data = self._source.get_data()
        return DataFrame(data)