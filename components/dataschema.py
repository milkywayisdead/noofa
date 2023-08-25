"""
Классы для схемы данных отчёта.
"""
from pandas import DataFrame

from ..core import collect_tables, get_source_class, Qbuilder
from .exceptions import SchemaComponentNotFound


class DataSchema:
    """
    Схема получения данных профиля.

    Содержит в себе значения по источникам, запросам и датафреймам,
    которые используются при формировании отчёта в классе ReportBuilder.
    """
    def __init__(self, sources=None, queries=None, dataframes=None, **kwargs):
        self._sources = sources if sources is not None else {}
        self._queries = queries if queries is not None else {}
        self._dataframes = dataframes if dataframes is not None else {}
        self._dataframes_by_name = {}

    def add_source(self, id=None, name='', type='', connection=None, **options):
        """
        Добавление источника в схему.
        """
        conn = connection
        if conn is None:
            source_cls = get_source_class(type)
            conn = source_cls(**options)
        self._sources[id] = SchemaSource(id=id, connection=conn, type=type, name=name)
        return self

    def add_query(self, id=None, name='', source=None, query_src=None,
        build_from='expression', **options):
        """
        Добавление запроса в схему.
        """
        name = name
        source_id = source
        src = self._sources[source_id]
        query_src = query_src
        build_from = build_from
        self._queries[id] = SchemaQuery(
            id, src, query_src, name=name, build_from=build_from)
        return self

    def add_dataframe(self, base=None, **options):
        """
        Добавление датафрейма в схему.
        """
        if base['type'] == 'query':
            source = self._sources.get(base['source'], None)
            query_id = base['value']
            query = self._queries[query_id]
            base['source'] = source
            base['query'] = query
        if base['type'] == 'source':
            source = self._sources.get(base['source'], None)
            base['source'] = source
        schema_dataframe = SchemaDataframe(base=base, **options)
        self._dataframes[schema_dataframe.id] = schema_dataframe
        self._dataframes_by_name[schema_dataframe.name] = schema_dataframe
        return self

    def get_source(self, source_id):
        source = self._sources.get(source_id, None)
        if source is None:
            raise SchemaComponentNotFound(source_id, 'source')
        return source

    def get_query(self, query_id):
        q = self._queries.get(query_id, None)
        if q is None:
            raise SchemaComponentNotFound(query_id, 'query')
        return q

    def get_dataframe(self, df_id):
        df = self._dataframes.get(df_id, None)
        if df is None:
            df = self._dataframes_by_name.get(df_id, None)
            if df is None:
                raise SchemaComponentNotFound(df_id, 'df')
        return df


class SchemaSource:
    """
    Источник в схеме профиля.
    """
    def __init__(self, id=None, type='', name='', connection=None, **kwargs):
        self.type = type
        self.id = id
        self.name = name
        self.connection = connection

    @property
    def is_opened(self):
        """
        Открыт ли источник (есть ли подключение).
        """
        return self.connection.connection is not None

    def open(self):
        """
        Открыть источник (соединение).
        """
        if not self.is_opened:
            self.connection.open()

    def close(self):
        self.connection.close()

    def test(self):
        self.connection.test()

    def get_table(self, table_name):
        """
        Построение объекта таблицы по имени.
        """
        self.open()
        return self.connection.get_table(table_name)

    def get_table_multiple(self, tables_list):
        self.open()
        return self.connection.get_table_multiple(tables_list)

    @property
    def is_sql(self):
        return self.connection.is_sql

    def get_data(self, query=None, **kwargs):
        source = self.connection
        if query is not None:
            if self.is_sql:
                return source.get_data(query=query)
            else:
                source.source = query['base']
                return source.get_data()
        return source.get_data()

    @property
    def wildcard(self):
        return self.connection.wildcard

    def __enter__(self):
        self.open()
        return self.connection

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()


class SchemaQuery:
    """
    Запрос в схеме профиля.
    """
    def __init__(self, id_, source=None, query_src=None,
        name='', build_from='expression', **kwargs):
        self.id = id_
        self.name = name
        self.query_src = query_src
        self.query = None
        self._source = source
        self._compiled = None
        self.build_from = build_from

    def execute(self):
        with self._source as source:
            if source.is_sql:
                self._compiled = self._compile()
                data = source.get_data(query=self._compiled)
            else:
                source.source = self.query_src['base']
                data = source.get_data()
            return data

    def _compile(self):
        """
        Создание объекта запроса (SelectQuery из noofa.core.conn.query).
        """
        query = self.query
        tables_list = collect_tables(query)
        source = self._source
        if not source.is_opened:
            source.open()
        tables = source.get_table_multiple(tables_list)
        qb_args = [tables, query, source.wildcard, source.connection.source_type == 'mssql']
        qbuilder = Qbuilder(*qb_args)
        return qbuilder.parse_query()


class SchemaDataframe:
    """
    Датафрейм в схеме профиля.
    """
    def __init__(self, id='', name='', base=None, dtypes=None, unions=None, joins=None,
        filters=None, ordering=None, columns=None, fillna=None, **options):
        self.id = id
        self.name = name
        self._build_type = base['type']
        self._build_from = base['value']
        self._source = base.get('source', None)
        self._query = base.get('query', None)
        self.dtypes = dtypes or []
        self.unions = unions or []
        self.joins = joins or []
        self.filters = filters or []
        self.ordering = ordering
        self.cols = columns or []
        self.fillna = fillna or []

    def get_data(self):
        if self.build_type == 'source':
            return self._source.get_data()
        data = self._query.execute()
        return data

    def build(self):
        res = self.get_data()
        if self.build_type == 'source':
            return res
        data, columns = res.data, res.columns
        return DataFrame(data, columns=columns)

    @property
    def build_type(self):
        return self._build_type

    @property
    def build_from(self):
        return self._build_from
