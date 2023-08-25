"""
Инструменты построения отчётов.
"""
import json
from io import BytesIO
from datetime import (
    date as dt_date,
    time as dt_time,
    datetime
)

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
    def __init__(self, data_config=None, components_config=None, values=None, set_evaluator=True, *args, **kwargs):
        data_config = data_config or {}
        components_config = components_config or {}
        values = values or {}

        self._dataschema = DataSchema()  # схема данных
        self._components_schema = ComponentsSchema()  # схема компонентов
        self.interpreter = Interpreter()  # интерпретатор для вычисления формул
        self.interpreter._connections = self._dataschema._sources
        self._compiled_queries = {}  #  сформированные запросы
        self._built_dataframes = {}  #  сформированные датафреймы
        self._results = {}  #  результаты запросов (полученные данные)
        self._df_stack = []  #  стэк id строящихся датафреймов

        sources_conf = data_config.get('sources', {})
        queries_config = data_config.get('queries', {})
        dataframes_config = data_config.get('dataframes', {})

        # добавление значений
        self.interpreter.add_values(values.values(), self)

        """
        добавление источников в схему:
        источники добавляются из словаря (json) либо из строки подключения (conn_str)
        либо из выражения (expression);
        в случае выражения внешней функцией должна быть функция create_connection:
        например, 'create_connection(тип_соединения, строка_подключения)'
        """
        for s in sources_conf.values():
            build_from, value = s['from'], s['value']
            opts = {'id': s['id'], 'name': s['name'], 'type': s['type']}
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
            opts = {
                'id': q['id'], 'name': q['name'], 'source': q['source'],
                'build_from': q['from'], 'query_src': q['value']
            }
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
        for c in components_config.values():
            type_ = c['type']
            if type_ == 'table':
                method = self._components_schema.add_table
            elif type_ == 'figure':
                method = self._components_schema.add_figure
            elif type_ == 'pivot_table':
                method = self._components_schema.add_pivot_table
            lo = c.get('layout', {})
            method(using_evaluator=evaluator, **c, **lo)

    def get_value(self, name):
        value = self.interpreter.get_value(name)
        return SingleValue(name, value)

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

    def apply_filters(self, filters):
        """
        Применить фильтры - т.е. задать для вычисляемых значений
        конфиги определённые значения.
        """
        for filter_key, filter_value in filters.items():
            self.interpreter.update_value(filter_key, filter_value)

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
        qf = query.build_from
        if qf == 'json':
            query.query = query.query_src
        elif qf == 'expression':
            query.query = self.evaluate(query.query_src).q_part
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
            res = self.get_data(df._query.id)
            dataframe = panda_builder.new(res.data, res.columns)
        elif build_type == 'expression':
            dataframe = self.evaluate(df.build_from)
        elif build_type == 'source':
            dataframe = df.get_data()
        return dataframe

    def build_dataframe(self, dataframe_id):
        """
        Сформировать датафрейм.

        dataframe_id - id датафрейма.
        """
        df = self.get_dataframe(dataframe_id)
        #  создание базового датафрейма - либо из запроса, либо из выражения
        dataframe = self.build_base(dataframe_id)

        # преобразование типов
        for dt in df.dtypes:
            try:
                col, dtype = dt['col'], dt['dtype']
                dataframe = panda_builder.astype(dataframe, col, dtype)
            except:
                pass

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
        extra_cols_n, extra_cols = len(df.cols), {}
        for col in df.cols:
            from_, col_name, expr = col['from'], col['name'], col['value']
            if from_ == 'expression':
                value = self.evaluate(expr)
            elif from_ == 'apply':
                value = self.interpreter.apply(dataframe, expr)
            if extra_cols_n == 1:
                dataframe = panda_builder.add_column(dataframe, col_name, value)
            else:
                extra_cols[col_name] = value
        if extra_cols:
            dataframe = panda_builder.add_columns(dataframe, extra_cols)

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
        orderings = {'cols': [], 'asc': []}
        for ordering in df.ordering:
            cols, asc = ordering['cols'], ordering['asc']
            orderings['cols'].append(cols)
            orderings['asc'].append(asc)
        if orderings['cols']:
            cols, asc = orderings['cols'], orderings['asc']
            dataframe = panda_builder.order_by(dataframe, cols, asc=asc)

        # обработка пустых значений
        for fn in df.fillna:
            col, action, value = fn['col'], fn['action'], fn['value']
            if action == 'drop':
                dataframe = panda_builder.drop_na(dataframe, col)
            elif action == 'fill':
                fill_value = self.evaluate(value)
                dataframe = panda_builder.fill_na(dataframe, col, fill_value)

        return dataframe

    def build_table(self, table, **kwargs):
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
        table.build(**kwargs)
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

    def bufferize_xlsx(self, cmp_type, cmp_id, **kwargs):
        """
        Получение содержимого результата запроса, датафрейма либо таблицы
        в виде буфера байт.
        """
        buffer = BytesIO()
        is_pt = False
        if cmp_type == 'dataframe':
            df = self.get_or_build_dataframe(cmp_id)
        elif cmp_type == 'query':
            data = self.get_data(cmp_id)
            df = panda_builder.new(data.data, data.columns)
        elif cmp_type == 'table':
            table = self.build_table(cmp_id, **kwargs)
            is_pt = hasattr(table, 'is_pivot_table')
            df = table.pivot_df if is_pt else table.df
        df.to_excel(buffer, index=is_pt)
        return buffer

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


class SingleValue:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    @property
    def is_simple(self):
        stypes = [
            str, int, float, bool, list,
            datetime, dt_date, dt_time,
        ]
        return type(self.value) in stypes
