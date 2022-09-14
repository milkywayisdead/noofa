from .core.func.errors import InterpreterContextError
from .core.func import Interpreter
from .components.dataschema import DataSchema
from .components.components import ComponentsSchema
from .core.dataframes import panda_builder


class ReportBuilder:
    """
    Формирователь отчётов.
    """
    def __init__(self, config_dict={}):
        self._dataschema = DataSchema()  # схема данных
        self._components_schema = ComponentsSchema()  # схема компонентов
        self.interpreter = Interpreter()  # интерпретатор для вычисления формул
        self.interpreter._connections = self._dataschema._sources
        self._compiled_queries = {}  #  сформированные запросы
        self._built_dataframes = {}  #  сформированные датафреймы
        self._results = {}  #  результаты запросов (полученные данные)
        sources_conf = config_dict.get('sources', {})
        queries_config = config_dict.get('queries', {})
        dataframes_config = config_dict.get('dataframes', {})
        for s in sources_conf.values():
            self._dataschema.add_source(**s)
        for q in queries_config.values():
            self._dataschema.add_query(**q)
        for df in dataframes_config.values():
            self._dataschema.add_dataframe(**df)

    def evaluate(self, expr):
        try: 
            return self.interpreter.evaluate(expr)
        except InterpreterContextError as e:
            df = self.build_dataframe(e.key)
            self.interpreter.add_to_global(e.key, df)
            return self.evaluate(expr)

    def apply(self, df_id, expr):
        df = self.build_dataframe(df_id)
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
            q = query.compile()
            self._compiled_queries[query.id] = q
            return q
        return query

    def get_data(self, query_id):
        if query_id in self._results:
            return self._results[query_id]
        query = self.get_query(query_id)
        data = query.execute()
        self._results[query.id] = data
        return data

    def build_dataframe(self, dataframe_id):
        """
        Сформировать датафрейм.
        """
        df = self._built_dataframes.get(dataframe_id, None)
        if df is not None:
            return df
        df = self.get_dataframe(dataframe_id)
        if not df.is_composite:
            dataframe = df.build()
        else:
            build_options = df.build_options
            build_type = build_options['type']
            if build_type == 'join':
                on = build_options['on']
                dataframes = build_options['dataframes']
                dataframes = [self.build_dataframe(df) for df in dataframes]
                dataframe = panda_builder.join(dataframes[0], dataframes[1], on)
            elif build_type == 'union':
                dataframes = build_options['dataframes']
                dataframes = [self.build_dataframe(df) for df in dataframes]
                dataframe = panda_builder.union(dataframes)
        if df.cols:
            for col in df.cols:
                col_name, expr = col['name'], col['value']
                value = self.interpreter.apply(dataframe, expr)
                dataframe = panda_builder.add_column(dataframe, col_name, value)
        if df.filters:
            dataframe = panda_builder.filter(dataframe, df.filters)
        if df.ordering:
            ordering = df.ordering
            cols, asc = ordering['cols'], ordering['asc']
            dataframe = panda_builder.order_by(dataframe, cols, asc=asc)
        self._built_dataframes[df.id] = dataframe
        return dataframe

    def df_to_dict(self, dataframe_id):
        """
        Датафрейм -> словарь.
        """
        df = self.build_dataframe(dataframe_id)
        return df.to_dict(orient='records')

    def get_source(self, source_id):
        return self._dataschema.get_source(source_id)

    def get_query(self, query_id):
        return self._dataschema.get_query(query_id)

    def get_dataframe(self, dataframe_id):
        return self._dataschema.get_dataframe(dataframe_id)


        

    