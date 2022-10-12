"""
Инструменты построения отчётов.
"""
import json

from ..core.func.errors import InterpreterContextError
from ..core.func import Interpreter
from ..components.dataschema import DataSchema
from ..components.components import ComponentsSchema
from ..core.dataframes import panda_builder
from .exceptions import RecursiveDataframeBuildError


class ReportBuilder:
    """
    Формирователь отчётов.
    """
    def __init__(self, config_dict={}, components_conf_dict={}, set_evaluator=True, *args, **kwargs):
        self._dataschema = DataSchema()  # схема данных
        self._components_schema = ComponentsSchema()  # схема компонентов
        self.interpreter = Interpreter()  # интерпретатор для вычисления формул
        self.interpreter._connections = self._dataschema._sources
        self._compiled_queries = {}  #  сформированные запросы
        self._built_dataframes = {}  #  сформированные датафреймы
        self._results = {}  #  результаты запросов (полученные данные)
        self._df_stack = []  #  стэк id строящихся датафреймов

        sources_conf = config_dict.get('sources', {})
        queries_config = config_dict.get('queries', {})
        dataframes_config = config_dict.get('dataframes', {})
        """
        добавление источников в схему:
        источники добавляются из словаря (json) либо из строки подключения (conn_str)
        либо из выражения (expression);
        в случае выражения внешней функцией должна быть функция create_connection:
        например, 'create_connection(тип_соединения, строка_подключения)'
        """
        for s in sources_conf.values():
            build_from, value = s['from'], s['value']
            opts = {'id': s['id'], 'type': s['type']}
            if build_from == 'json':
                opts.update(value)
            elif build_from == 'conn_str':
                opts['conn_str'] = value
            elif build_from == 'expression':
                conn = self.evaluate(value)
                opts['connection'] = conn
            self._dataschema.add_source(**opts)

        """
        добавление источников в схему:
        источники добавляются из словаря (json) либо из выражения (expression);
        выражение должно состоять из функции sql_select, например:
        'sql_select("table1", sql_join("table2", "table1", "field1", "field2"))'.
        """
        for q in queries_config.values():
            opts = {'id': q['id'], 'source': q['source']}
            build_from, value = q['from'], q['value']
            if build_from == 'json':
                opts['query'] = value
            elif build_from == 'expression':
                opts['query'] = self.evaluate(value).q_part
            self._dataschema.add_query(**opts)

        # добавление датафреймов в схему
        for df in dataframes_config.values():
            opts = {**df}
            self._dataschema.add_dataframe(**opts)

        # добавление компонентов в схему компонентов,
        # если параметр set_evaluator равен True, то для компонентов
        # в качестве параметра "вычислителя" задаётся сам ReportBuilder
        if set_evaluator == True:
            evaluator = self
        else:
            evaluator = None
        for c in components_conf_dict.values():
            type_ = c['type']
            if type_ == 'table':
                method = self._components_schema.add_table
            elif type_ == 'figure':
                method = self._components_schema.add_figure
            lo = c.pop('layout')
            method(using_evaluator=evaluator, **c, **lo)

    def evaluate(self, expr):
        """
        Вычисление значения по строке выражения.
        """
        try: 
            return self.interpreter.evaluate(expr)
        except InterpreterContextError as e:
            df = self.get_or_build_dataframe(e.key)
            self.interpreter.add_to_global(e.key, df)
            return self.evaluate(expr)

    def apply(self, df_id, expr):
        """
        Применение выражения к строкам датафрейма.
        """
        df = self.get_or_build_dataframe(df_id)
        return self.interpreter.apply(df, expr)

    @property
    def dataframes(self):
        return self._dataschema._dataframes

    def build_query(self, query_id):
        """
        Сформировать объект запроса.
        """
        query = self._compiled_queries.get(query_id, None)
        if query is None:
            query = self.get_query(query_id)
            q = query._compile()
            self._compiled_queries[query.id] = q
            return q
        return query

    def get_data(self, query_id):
        """
        Получение данных по запросу.
        query_id - id запроса.
        Если данные имеются в self._result, то будут возвращены они,
        в противном случае выполняется запрос, после чего рез. вносится в self._results. 
        """
        if query_id in self._results:
            return self._results[query_id]
        query = self.get_query(query_id)
        data = query.execute()
        self._compiled_queries[query.id] = query._compiled
        self._results[query.id] = data
        return data

    def get_or_build_dataframe(self, dataframe_id):
        """
        Получить сформированный либо сформировать датафрейм.
        """

        # проверка на рекурсивные вызовы при построении -
        # если в конфиге задано построение дф по своим же данным,
        # то выбрасывается ошибка
        if dataframe_id in self._df_stack:
            self._df_stack.clear()  # очистить стэк дф в случае ошибки
            raise RecursiveDataframeBuildError(dataframe_id)

        self._df_stack.append(dataframe_id)  # кладём id дф в стэк

        #  пробуем получить готовый дф, если его нет, то собираем с нуля
        df = self._built_dataframes.get(dataframe_id, None)
        if df is None:
            df = self.build_dataframe(dataframe_id)

        #  добавляем в словарь готовых дф для возможного последующего использования
        self._built_dataframes[dataframe_id] = df

        # удаляем id дф из стэка
        self._df_stack.pop()
        
        return df

    def build_base(self, dataframe_id):
        """
        Построение основы датафрейма.

        dataframe_id - id датафрейма.
        """
        df = self.get_dataframe(dataframe_id)
        build_type = df.build_type
        if build_type == 'query':
            dataframe = panda_builder.new(df.get_data())
        elif build_type == 'expression':
            dataframe = self.evaluate(df.build_from)
        return dataframe

    def build_dataframe(self, dataframe_id):
        """
        Сформировать датафрейм.

        dataframe_id - id датафрейма.
        """
        df = self.get_dataframe(dataframe_id)
        #  создание базового датафрейма - либо из запроса, либо из выражения
        dataframe = self.build_base(dataframe_id)

        #  приклеивание других датафреймов
        for u in df.unions:
            from_, value = u['from'], u['value']
            if from_ == 'expression':
                df2 = self.evaluate(value)
            else:
                df2 = self.get_or_build_dataframe(value)
            dataframe = panda_builder.union([dataframe, df2])

        #  добавление соединений с другими датафреймами
        for j in df.joins:
            from_, value = j['from'], j['value']
            on, join_type = j['on'], j['type']
            if from_ == 'expression':
                df2 = self.evaluate(value)
            else:
                df2 = self.get_or_build_dataframe(value)
            dataframe = panda_builder.join(dataframe, df2, on, join_type)

        #  добавление новых столбцов либо изменение существующих
        for col in df.cols:
            from_, col_name, expr = col['from'], col['name'], col['value']
            if from_ == 'expression':
                value = self.evaluate(expr)
            elif from_ == 'apply':
                value = self.interpreter.apply(dataframe, expr)
            dataframe = panda_builder.add_column(dataframe, col_name, value)

        #  применение фильтров
        filters = []
        for f in df.filters:
            from_, filter_ = f['from'], f['value']
            if from_ == 'expression':
                filter_ = self.evaluate(filter_).df_filter
            filters.append(filter_)
        if filters:
            dataframe = panda_builder.filter(dataframe, filters)

        #  упорядочивание
        if df.ordering:
            ordering = df.ordering
            cols, asc = ordering['cols'], ordering['asc']
            dataframe = panda_builder.order_by(dataframe, cols, asc=asc)
        return dataframe

    def build_table(self, table):
        """
        Формирование компонента-таблицы.
        table - id компонента в наборе таблиц схемы компонентов
        либо экземпляр компонента-таблицы.
        """
        if isinstance(table, str):
            table = self._components_schema.get_table(table)
        #  если у компонента нет "объекта-вычислителя",
        #  то им становится сам ReportBuilder    
        if table.evaluator is None:
            table.evaluator = self
        table.build()
        return table

    def build_figure(self, figure):
        """
        Формирование компонента-графика.
        figure - id компонента в наборе графиков схемы компонентов
        либо экземпляр компонента-графика.
        """
        if isinstance(figure, str):
            figure = self._components_schema.get_figure(figure)
        if figure.evaluator is None:
            figure.evaluator = self
        _ = figure.build()
        return figure

    def build_component(self, component):
        if isinstance(component, str):
            component = self.get_component(component)
        method = getattr(self, f'build_{component.type}')
        return method(component)

    def df_to_dict(self, dataframe_id):
        """
        Датафрейм -> словарь.
        """
        df = self.get_or_build_dataframe(dataframe_id)
        return df.to_dict(orient='records')

    def get_source(self, source_id):
        return self._dataschema.get_source(source_id)

    def get_query(self, query_id):
        return self._dataschema.get_query(query_id)

    def get_dataframe(self, dataframe_id):
        return self._dataschema.get_dataframe(dataframe_id)

    def get_component(self, component_id):
        return self._components_schema.get_component(component_id)


class CachingReportBuilder(ReportBuilder):
    """
    Формирователь отчётов с функционалом кэширования в redis.
    Это дочерний класс от ReportBuilder с измененными методами get_or_build_dataframe и
    get_data и несколькими дополнительными методами, связанными с кэшированием.
    При создании датафрейма кэшируется его содержимое в виде словаря. При построении
    датафрейма сначала делается попытка получить кэшированное содержимое для датафрейма,
    в случае отсутствия такового - выполняется построение с нуля.
    В конструктор, помимо параметров подключения, можно передавать аргумент prefix вида 'profileN', 
    где N - id профиля отчёта.
    """
    def __init__(self, *args, **kwargs):
        defaults = {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'ex': 300,
            'prefix': 'profile0',
        }
        for kw in defaults.keys():
            if kw in kwargs:
                defaults[kw] = kwargs.pop(kw)

        super().__init__(*args, **kwargs)
        self._redis_host = defaults['host']
        self._redis_port = defaults['port']
        self._redis_db = defaults['db']
        self._prefix = defaults['prefix']
        self._ex = defaults['ex']  # время жизни кэшированных записей в секундах
        self._conn = None

    def get_or_build_dataframe(self, dataframe_id):
        #  сначала пробуем получить уже готовый дф
        df = self._built_dataframes.get(dataframe_id, None)
        #  если его нет, то пробуем построить его по данным из кэша
        if df is None:
            cached_df = self.get_cached_df(dataframe_id)
            if cached_df:
                df = panda_builder.new(cached_df)
            #  если в кэше данных нет - строим дф заново 
            else:
                df = self.build_dataframe(dataframe_id)

        #  добавляем в словарь готовых дф для возможного последующего использования,
        #  чтобы не обращаться дополнительно к кэшу
        self._built_dataframes[dataframe_id] = df

        #  кэшируем дф для возможного последующего использования его данных другими
        #  экземплярами CachingReportBuilder
        self.cache_df(dataframe_id, df)

        return df

    def get_data(self, query_id):
        #  сначала проверяем наличие рез. запроса в сохраненных результатах -
        #  в self._results
        if query_id in self._results:
            data = self._results[query_id]
        else:
            #  если их там нет - пробуем получить из кэша
            data = self.get_cached_query_result(query_id)
        #  если в кэше нет результата - выполняем запрос заново
        if data is None:
            data = super().get_data(query_id)

        #  кэшируем для возможного послед. использования
        self.cache_query_result(query_id, data)
        return data

    def _connect(self):
        """
        Создание соединения с redis.
        """
        self._conn = redis.Redis(
            host=self._redis_host, 
            port=self._redis_port, 
            db=self._redis_db,
        )

    def _set(self, key, value, value_type='dataframe', ex=None):
        """
        Установка значения в кэш.
        """
        if self._conn is None:
            self._connect()
        _key = f'{self._prefix}:{value_type}:{key}'
        if ex is None:
            ex = self._ex
        self._conn.set(_key, value, ex=ex)

    def _get(self, key, value_type='dataframe'):
        """
        Получение значения из кэша.
        """
        if self._conn is None:
            self._connect()
        return self._conn.get(f'{self._prefix}:{value_type}:{key}')

    def cache_df(self, dataframe_id, df, ex=None):
        """
        Кэшировать датафрейм.
        dataframe_id - id датафрейма,
        df - экз. pandas.DataFrame либо словарь,
        ex - время хранения в кэше в секундах.
        """
        if isinstance(df, panda_builder.pd.DataFrame):
            df = df.to_dict(orient='records')
        df = json.dumps(df)
        self._set(dataframe_id, df, value_type='dataframe', ex=ex)

    def get_cached_df(self, dataframe_id):
        """
        Получение кэшированных данных датафрейма.
        dataframe_id - id датафрейма.
        """
        cached_df = self._get(dataframe_id, value_type='dataframe')
        if cached_df:
            cached_df = json.loads(cached_df)
            return cached_df

    def cache_query_result(self, query_id, query_result, ex=None):
        """
        Кэшировать результат запроса.
        query_id - id запроса,
        query_result - результат запроса в виде списка словарей,
        ex - время хранения в кэше в секундах.
        """
        if isinstance(query_result, list):
            query_result = json.dumps(query_result)
        self._set(query_id, query_result, value_type='query', ex=ex)

    def get_cached_query_result(self, query_id):
        """
        Получение кэшированных результатов запроса.
        query_id - id запроса.
        """
        cached_qr = self._get(query_id, value_type='query')
        if cached_qr:
            cached_qr = json.loads(cached_qr)
            return cached_qr