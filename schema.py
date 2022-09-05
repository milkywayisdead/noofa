"""
Для профилей отчётов.
"""
from pandas import DataFrame

from .utils import get_source_class, collect_tables, Qbuilder, panda
from .utils import panda


class DataSchema:
    """
    Схема получения данных профиля.
    """
    def __init__(self, **kwargs):
        self._sources = kwargs.get('sources', {})
        self._queries = kwargs.get('queries', {})
        self._dataframes = kwargs.get('dataframes', {})

    def add_source(self, **options):
        id_ = options.pop('id')
        type_ = options.pop('type')
        source_cls = get_source_class(type_)
        conn = source_cls(**options)
        self._sources[id_] = SchemaSource(id_, connection=conn)
        return self

    def add_query(self, **options):
        id_ = options['id']
        source_name = options['source']
        source = self._sources[source_name]
        query_as_json = options['query']
        self._queries[id_] = SchemaQuery(id_, query_as_json, source)
        return self

    def add_dataframe(self, **options):
        id_ = options['id']
        is_composite = options.get('composite', False)
        if is_composite:
            dataframes = []
            dataframes_list = options['build']['dataframes']
            for df in dataframes_list:
                dataframes.append(self._dataframes[df])
            options['build']['dataframes'] = dataframes
            options['source'] = None
            options['query'] = None
            self._dataframes[id_] = SchemaDataframe(id_, **options)
        else:
            source = self._sources[options['source']]
            if not source.is_sql:
                query = None
            else:
                query = self._queries[options['query']]
            self._dataframes[id_] = SchemaDataframe(id_, source, query)
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
    def __init__(self, id_, **kwargs):
        self.id = id_
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

    def __enter__(self):
        self.open()
        return self.connection

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()


class SchemaQuery:
    """
    Запрос в схеме профиля.
    """
    def __init__(self, id_, query_as_json, source=None):
        self.id = id_
        self._query_as_json = query_as_json
        self._source = source

    def execute(self):
        with self._source as source:
            query = self._compile()
            data = source.get_data(query=query)
            return data

    def _compile(self):
        """
        Создание объекта запроса (SelectQuery из noofa.core.conn.query).
        """
        query = self._query_as_json
        tables_list = collect_tables(query)
        tables = {t: self._source.get_table(t) for t in tables_list}
        qbuilder = Qbuilder(tables, query)
        return qbuilder.parse_query()


class SchemaDataframe:
    """
    Датафрейм в схеме профиля.
    """
    def __init__(self, id_, source, query=None, **options):
        self.id = id_
        self._source = source
        self._query = query
        self.is_composite = options.get('composite', False)
        self._build_type = None
        self._dataframes = []
        if self.is_composite:
            self._build_type = options['build']['type']
            self._dataframes = options['build']['dataframes']
            if self._build_type == 'join':
                self._on = options['build']['on']

    def get_data(self):
        if self._source.is_sql:
            data = self._query.execute()
        else:
            data = self._source.get_data()
        return data
        
    def compile(self):
        if self.is_composite:
            build_type = self._build_type
            if build_type == 'union':
                dataframes = [df.compile() for df in self._dataframes]
                return panda.union(dataframes)
            elif build_type == 'join':
                on = self._on
                dataframes = [df.compile() for df in self._dataframes]
                return panda.join(dataframes[0], dataframes[1], on)
        else:
            data = self.get_data()
        return DataFrame(data)