"""
Классы для схемы данных отчёта.
"""
from pandas import DataFrame

from ..core import collect_tables, get_source_class, Qbuilder


class DataSchema:
    """
    Схема получения данных профиля.

    Содержит в себе значения по источникам, запросам и датафреймам,
    которые используются при формировании отчёта в классе ReportBuilder.
    """
    def __init__(self, **kwargs):
        self._sources = kwargs.get('sources', {})
        self._queries = kwargs.get('queries', {})
        self._dataframes = kwargs.get('dataframes', {})

    def add_source(self, **options):
        """
        Добавление источника в схему.
        """
        id_ = options.pop('id')
        type_ = options.pop('type')
        conn = options.get('connection', None)
        if conn is None:
            source_cls = get_source_class(type_)
            conn = source_cls(**options)
        self._sources[id_] = SchemaSource(id_, connection=conn, type=type_)
        return self

    def add_query(self, **options):
        """
        Добавление запроса в схему.
        """
        id_ = options['id']
        source_name = options['source']
        source = self._sources[source_name]
        query_as_json = options['query']
        self._queries[id_] = SchemaQuery(id_, query_as_json, source)
        return self

    def add_dataframe(self, **options):
        """
        Добавление датафрейма в схему.
        """
        id_ = options['id']
        base = options['base']
        if base['type'] == 'query':
            source = self._sources.get(base['source'], None)
            query_id = base['value']
            if not source.is_sql:
                query = None
            else:
                query = self._queries[query_id]
            base['source'] = source
            base['query'] = query
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
        self.type = kwargs.get('type', '')
        self.id = id_
        self.connection = kwargs.get('connection', None)

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

    def get_table(self, table_name):
        """
        Построение объекта таблицы по имени.
        """
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
        self._compiled = None

    def execute(self):
        with self._source as source:
            self._compiled = self._compile()
            data = source.get_data(query=self._compiled)
            return data

    def _compile(self):
        """
        Создание объекта запроса (SelectQuery из noofa.core.conn.query).
        """
        query = self._query_as_json
        tables_list = collect_tables(query)
        source = self._source
        if not source.is_opened:
            source.open()
        tables = {t: source.get_table(t) for t in tables_list}
        qb_args = [tables, query]
        if source.type == 'sqlite':
            qb_args.append('?')
        qbuilder = Qbuilder(*qb_args)
        return qbuilder.parse_query()


class SchemaDataframe:
    """
    Датафрейм в схеме профиля.
    """
    def __init__(self, **options):
        self.id = options['id']
        self._build_type = options['base']['type']
        self._build_from = options['base']['value'] 
        self._source = options['base'].get('source', None)
        self._query = options['base'].get('query', None)
        self.unions = options.get('unions', [])
        self.joins = options.get('joins', [])
        self.filters = options.get('filters', [])
        self.ordering = options.get('ordering', None)
        self.cols = options.get('columns', [])

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
    def build_type(self):
        return self._build_type

    @property
    def build_from(self):
        return self._build_from