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
        source = self._sources.get(options['source'], None)
        query = options.get('query', None)
        if source is None and query is None:
            options['source'], options['query'] = None, None
            self._dataframes[id_] = SchemaDataframe(**options)
            return self
        if not source.is_sql:
            query = None
        else:
            if not query is None:
                query = self._queries[query]
        options['source'] = source
        options['query'] = query
        self._dataframes[id_] = SchemaDataframe(**options)
        return self     

    def get_source(self, source_id):
        return self._sources[source_id]

    def get_query(self, query_id):
        return self._queries[query_id]

    def get_dataframe(self, df_id):
        return self._dataframes[df_id]


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
    def __init__(self, **options):
        self.id = options['id']
        self._source = options.get('source', None)
        self._query = options.get('query', None)
        self.is_composite = options.get('composite', False)
        if self.is_composite:
            self._build = options['build']

    def get_data(self):
        if self._source.is_sql:
            data = self._query.execute()
        else:
            data = self._source.get_data()
        return data
        
    def build(self):
        data = self.get_data()
        return DataFrame(data)

    @property
    def build_options(self):
        return self._build